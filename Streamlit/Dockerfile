FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Streamlitのアプリケーションファイルのパスを修正
COPY ./app /app

CMD ["streamlit", "run", "streamlit_app.py"]
