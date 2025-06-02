from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import httpx
import datetime

app = FastAPI()
visit_logs = []  # 🔄 메모리 내 접속 로그 저장 (재시작 시 초기화됨)

# 📍 위치정보 수집 함수
async def get_geo_info(ip: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://ip-api.com/json/{ip}")
            return response.json()
    except:
        return {}

# 🔍 방문자 추적
@app.get("/", response_class=HTMLResponse)
async def track_and_show(request: Request):
    ip = request.client.host
    user_agent = request.headers.get("user-agent", "Unknown")
    geo = await get_geo_info(ip)
    country = geo.get("country", "Unknown")
    city = geo.get("city", "Unknown")
    now = datetime.datetime.now().isoformat()

    # 📥 메모리에 기록
    visit_logs.append([now, ip, user_agent, country, city])
    if len(visit_logs) > 500:
        visit_logs.pop(0)  # 오래된 기록 삭제

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

# 📋 로그 확인
@app.get("/log", response_class=HTMLResponse)
async def show_logs():
    headers = ["시간", "IP", "브라우저", "국가", "도시"]

    log_html = "<table border='1' cellpadding='5'><tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr>"
    for row in visit_logs[-100:]:
        log_html += "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
    log_html += "</table>"

    html = f"""
    <html>
        <head><meta charset='UTF-8'><title>방문자 로그</title></head>
        <body style='font-family:sans-serif;padding:40px;'>
            <h2>📋 방문자 로그 (최근 {len(visit_logs)}명)</h2>
            {log_html}
        </body>
    </html>
    """
    return HTMLResponse(content=html)
