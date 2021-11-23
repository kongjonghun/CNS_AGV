# 서버 실행 방법
### local 실행시)
- python app.py localhost
- python app.py
### aws 실행시)
- python app.py 0.0.0.0

주소창에 http://해당ip주소:5000 입력 시
'Hello, World!' 보이면 실행 중

# 클라이언트 실행 방법
python client.py AGV_NO
ex) python client.py AGV00001

# Monitoring 실행 방법
local)
http://localhost:5000/monitoring

aws)
http://서버ip주소:5000/monitoring
