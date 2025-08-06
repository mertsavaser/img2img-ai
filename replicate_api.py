import os
import requests
import io
import base64
import time
from PIL import Image
from dotenv import load_dotenv

# Ortam değişkenlerini yükle
load_dotenv()
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# Replicate API endpoint ve header bilgileri
REPLICATE_ENDPOINT = "https://api.replicate.com/v1/predictions"
HEADERS = {
    "Authorization": f"Token {REPLICATE_API_TOKEN}",
    "Content-Type": "application/json",
}

# Replicate sürüm ID'si (Stable Diffusion)
REPLICATE_MODEL_VERSION = "a9758cb0d1b05920e61a11558869b5a3fe2549f23402d408b7879b3c5cddc1b1"

def replicate_img2img_generate(init_image: Image.Image, prompt: str, strength: float = 0.6, guidance_scale: float = 7.5):
    """
    Replicate üzerinden img2img görsel üretimi yapar.
    """
    # Token kontrolü
    if not REPLICATE_API_TOKEN:
        return None, "❌ REPLICATE_API_TOKEN bulunamadı. `.env` dosyasını kontrol et."

    # Girdi kontrolü
    if init_image is None or not prompt:
        return None, "⚠️ Görsel ve prompt girmeniz gerekiyor."

    try:
        # Görseli base64'e çevir
        buffered = io.BytesIO()
        init_image.save(buffered, format="PNG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        image_uri = f"data:image/png;base64,{image_base64}"

        # API isteği verisi
        data = {
            "version": REPLICATE_MODEL_VERSION,
            "input": {
                "image": image_uri,
                "prompt": prompt,
                "strength": strength,
                "guidance_scale": guidance_scale,
            }
        }

        # API çağrısı
        response = requests.post(REPLICATE_ENDPOINT, headers=HEADERS, json=data)
        if response.status_code != 201:
            return None, f"❌ API Hatası: {response.status_code} - {response.text}"

        # Sonuç URL'si
        prediction_url = response.json()["urls"]["get"]

        # 60 saniyeye kadar sonucu bekle
        start_time = time.time()
        while True:
            poll = requests.get(prediction_url, headers=HEADERS).json()

            if poll["status"] == "succeeded":
                output_url = poll["output"]
                image_response = requests.get(output_url)
                return Image.open(io.BytesIO(image_response.content)), "✅ Başarılı!"

            elif poll["status"] == "failed":
                return None, "❌ Görsel üretimi başarısız oldu."

            elif time.time() - start_time > 60:
                return None, "❌ Zaman aşımı: Replicate yanıt vermedi."

            time.sleep(1)

    except Exception as e:
        return None, f"❌ Replicate üretim hatası: {str(e)}"
