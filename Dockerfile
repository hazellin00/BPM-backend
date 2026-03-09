# 1. 使用官方 Python 3.10 輕量版作為基礎映像檔
FROM python:3.10-slim

# 2. 設定容器內的工作目錄
WORKDIR /app

# 3. 避免 Python 產生 .pyc 檔案並強制輸出日誌，方便在 Render 上除錯
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 4. 安裝系統依賴（如果你的套件需要編譯環境，雖然 FastAPI 通常不需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 5. 複製相依套件清單
COPY requirements.txt .

# 6. 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 7. 複製所有後端程式碼到容器內
COPY . .

# 8. 告知 Docker 容器將監聽 Port 80
EXPOSE 80

# 9. 啟動 FastAPI 服務
# 這裡使用 uvicorn 啟動，並綁定到 0.0.0.0 確保 Render 能從外部存取
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]