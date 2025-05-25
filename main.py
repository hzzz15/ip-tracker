from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import httpx
import datetime
import csv
import os

app = FastAPI()

LOG_FILE = "visitor_log.csv"

# CSV 파일이 없으면 헤더 추가 생성
def init_log_file():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "ip", "user_agent", "country", "city"])

init_log_file()

# 위치정보 수집 함수
async def get_geo_info(ip: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://ip-api.com/json/{ip}")
            return response.json()
    except:
        return {}

@app.get("/", response_class=HTMLResponse)
async def track_and_show(request: Request):
    ip = request.client.host
    user_agent = request.headers.get("user-agent", "Unknown")
    geo = await get_geo_info(ip)
    country = geo.get("country", "Unknown")
    city = geo.get("city", "Unknown")
    now = datetime.datetime.now().isoformat()

    # CSV에 로그 저장
    with open(LOG_FILE, "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([now, ip, user_agent, country, city])

    html = f"""
    <html>
        <head><meta charset='UTF-8'><title>시스템 경고</title></head>
        <body style='background-color:#000; color:#ff4c4c; font-family:sans-serif; padding:40px;'>
            <h1>⚠️ 시스템 보안 경고 ⚠️</h1>
            <p>당신의 접속 정보는 이미 서버에 저장되었습니다.</p>
            <ul>
                <li><strong>IP 주소:</strong> {ip}</li>
                <li><strong>브라우저 정보:</strong> {user_agent}</li>
                <li><strong>위치:</strong> {country}, {city}</li>
                <li><strong>접속 시각:</strong> {now}</li>
            </ul>
        </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.get("/log", response_class=HTMLResponse)
async def show_logs():
    if not os.path.exists(LOG_FILE):
        return HTMLResponse("<html><body><p>No logs yet.</p></body></html>")

    rows = []
    with open(LOG_FILE, "r") as f:
        reader = csv.reader(f)
        headers = next(reader)
        for row in reader:
            rows.append(row)

    log_html = "<table border='1' cellpadding='5'><tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr>"
    for row in rows[-100:]:  # 최근 100개만
        log_html += "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
    log_html += "</table>"

    html = f"""
    <html>
        <head><meta charset='UTF-8'><title>방문자 로그</title></head>
        <body style='font-family:sans-serif;padding:40px;'>
            <h2>📋 방문자 로그 (경쟁 {len(rows)}명)</h2>
            {log_html}
        </body>
    </html>
    """
    return HTMLResponse(content=html)