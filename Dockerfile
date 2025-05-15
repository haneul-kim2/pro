# Dockerfile (Cloud Run 배포용)

# 1. 베이스 이미지: Python 3.12 슬림 버전을 사용합니다.
FROM python:3.12-slim

# 2. 작업 디렉토리: 컨테이너 안에서 명령이 실행될 기본 폴더를 /app으로 설정합니다.
WORKDIR /app

# 3. requirements.txt 파일 복사:
# 먼저 이 파일만 복사해서 라이브러리를 설치하면, 나중에 코드만 바뀌었을 때 Docker 빌드 시간을 단축할 수 있습니다.
COPY requirements.txt requirements.txt

# 4. Python 라이브러리 설치:
# requirements.txt에 있는 모든 라이브러리를 컨테이너 안에 설치합니다.
RUN pip install --no-cache-dir -r requirements.txt

# 5. 프로젝트 전체 파일 복사:
# 현재 Dockerfile이 있는 폴더(로컬 PC의 C:\pro\)의 모든 파일과 폴더를
# 컨테이너 안의 /app 폴더로 복사합니다.
COPY . .

# 6. 포트 설정:
# 컨테이너가 8080 포트에서 요청을 받을 것이라고 알려줍니다.
# Cloud Run은 이 내부 포트를 외부에서 접속 가능한 HTTPS(443) 포트로 자동 연결해줍니다.
EXPOSE 8080

# 7. (중요) PYTHONPATH 환경 변수 설정:
# main.py에서 'from app import ...' 와 같이 app 폴더 내의 모듈을 가져올 수 있도록 설정합니다.
ENV PYTHONPATH=/app

# 8. 애플리케이션 실행 명령어:
# 컨테이너가 시작될 때 실행될 명령어입니다.
# Gunicorn을 사용하여 Uvicorn 워커로 main.py 안의 FastAPI app 인스턴스를 실행합니다.
# Cloud Run은 PORT 환경 변수를 자동으로 제공하며, Gunicorn이 이를 사용하게 됩니다.
# 여기서는 명시적으로 8080 포트에 바인딩합니다.
CMD ["gunicorn", "main:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080"]