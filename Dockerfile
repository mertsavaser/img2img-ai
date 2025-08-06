# Python 3.10 slim imajı
FROM python:3.10-slim

# Log'ları anlık görmek için
ENV PYTHONUNBUFFERED=1

# Sisteme gerekli temel paketleri kur
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Çalışma klasörünü oluştur
WORKDIR /app

# requirements.txt'yi kopyala
COPY requirements.txt .

# pip'i güncelle + bağımlılıkları kur
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org \
    -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# Port aç
EXPOSE 7860

# Başlangıç komutu
CMD ["python", "img2img_app.py"]
