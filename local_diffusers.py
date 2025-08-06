import torch
from diffusers import StableDiffusionImg2ImgPipeline
from PIL import Image

# Cihaz ve dtype tespiti
device = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.float16 if device == "cuda" else torch.float32

# Pipeline önbelleği
pipe = None

def load_pipeline():
    global pipe
    if pipe is None:
        try:
            pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                torch_dtype=dtype
            ).to(device)
        except Exception as e:
            print(f"❌ Model yüklenirken hata oluştu: {e}")
            pipe = None

# Yerel Img2Img üretim fonksiyonu
def local_img2img_generate(init_image, prompt, strength=0.75, guidance_scale=7.5):
    global pipe
    if pipe is None:
        load_pipeline()
        if pipe is None:
            return None, "❌ Model yüklenemedi. Lütfen uygulamayı yeniden başlat."

    if init_image is None or not prompt:
        return None, "⚠️ Görsel ve prompt girmeniz gerekiyor."

    try:
        # Görseli normalleştir
        init_image = init_image.convert("RGB")
        init_image = init_image.resize((512, 512))

        # Görsel üretimi
        output = pipe(
            prompt=prompt,
            image=init_image,
            strength=strength,
            guidance_scale=guidance_scale
        )

        if not output or not output.images:
            return None, "❌ Görsel üretilemedi."

        return output.images[0], "✅ Başarılı!"
    except Exception as e:
        return None, f"❌ Lokal üretim hatası: {str(e)}"
