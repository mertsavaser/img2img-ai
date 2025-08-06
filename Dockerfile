# ✅ Python 3.10 slim imajı
FROM python:3.10-slim

# ✅ Log'ları anlık görebilmek için
ENV PYTHONUNBUFFERED=1

# ✅ Gerekli sistem paketleri
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# ✅ Çalışma dizini
WORKDIR /app

# ✅ requirements.txt'yi kopyala ve kur
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org \
    -r requirements.txt

# ✅ Tüm uygulama dosyalarını kopyala
COPY . .

# ✅ Port aç
EXPOSE 7860

# ✅ Başlangıç komutu
CMD ["python", "img2img_app.py"]
