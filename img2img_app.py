import os
import gradio as gr
from dotenv import load_dotenv
from PIL import Image
import torch
import GPUtil

from replicate_api import replicate_img2img_generate
from local_diffusers import local_img2img_generate

# Ortam değişkenlerini yükle
load_dotenv()

# Donanım bilgisi
device = "cuda" if torch.cuda.is_available() else "cpu"
gpus = GPUtil.getGPUs()
vram = f"{gpus[0].memoryTotal:.1f} GB" if gpus else "N/A"
model_name = "runwayml/stable-diffusion-v1-5"

# Stil Prompt Map
style_map = {
    "None": "",
    "Realistic": "ultra realistic, 8k DSLR photo",
    "Anime": "anime style, cel shading, colorful",
    "Cyberpunk": "cyberpunk world, neon lights, dystopia",
    "Pixel Art": "8-bit pixel art, low-res, retro",
    "3D Render": "cinematic 3D render, octane lighting"
}

# Preset Promptlar
preset_prompts = {
    "🧑‍🚀 Astronot": "astronaut floating in space, high detail, sci-fi scene",
    "🧠 AI Mühendisi": "futuristic AI engineer, glowing circuits, neon lights",
    "🦸 Süper Kahraman": "heroic male character, cinematic lighting, comic style"
}

def generate_image(init_image, prompt, mode, style, strength, guidance):
    if init_image is None or not prompt:
        return None, "⚠️ Görsel ve prompt girmen lazım."

    style_prompt = style_map.get(style, "")
    full_prompt = f"{style_prompt}, {prompt}" if style_prompt else prompt

    try:
        if mode == "Replicate":
            return replicate_img2img_generate(init_image, full_prompt)
        elif mode == "Lokal":
            return local_img2img_generate(init_image, full_prompt, strength, guidance)
        else:
            return None, "⚠️ Geçersiz mod seçimi!"
    except Exception as e:
        return None, f"❌ Hata oluştu: {str(e)}"

def generate_and_save(init_image, prompt, mode, style, strength, guidance, gallery_images):
    image, msg = generate_image(init_image, prompt, mode, style, strength, guidance)
    if image:
        os.makedirs("outputs", exist_ok=True)
        output_path = f"outputs/output_{torch.randint(0,99999,(1,)).item()}.png"
        image.save(output_path)
        gallery_images.append(image)
        return image, msg, gallery_images
    else:
        return None, msg, gallery_images

with gr.Blocks(theme=gr.themes.Soft(), css="body { background-color: #f7f7f7; font-family: 'Segoe UI', sans-serif; } .gradio-container { max-width: 1000px; margin: auto; }") as demo:
    gr.Markdown(f"""
    # 🎨 AI IMG2IMG Generator
    `Replicate` (API) veya `Lokal` modda görüntü dönüştür.  
    **🧠 Model:** `{model_name}` | **💻 Cihaz:** `{device}` | **🧠 VRAM:** `{vram}` 
    """)
    
    gallery_state = gr.State([])

    with gr.Row():
        with gr.Column():
            prompt = gr.Textbox(label="🎯 Prompt", placeholder="Örn: futuristic dog in armor", lines=2)

            with gr.Row():
                for label, value in preset_prompts.items():
                    gr.Button(label, scale=0.5, min_width=100).click(lambda v=value: v, outputs=prompt)

            init_image = gr.Image(label="🖼️ Başlangıç Görseli", type="pil")
            mode = gr.Radio(["Replicate", "Lokal"], label="⚙️ Mod Seç", value="Lokal")
            style = gr.Dropdown(list(style_map.keys()), value="None", label="🎨 Stil Seç")

            with gr.Accordion("🔧 Gelişmiş Ayarlar", open=False):
                strength = gr.Slider(0.0, 1.0, value=0.75, label="🎚️ Strength (giriş görseline sadakat)")
                guidance = gr.Slider(0.0, 20.0, value=7.5, label="🎯 Guidance Scale (prompt'a uyum)")

            generate_btn = gr.Button("🧠 Görseli Oluştur")

        with gr.Column():
            output_image = gr.Image(label="🎨 Üretilen Görsel")
            status = gr.Textbox(label="ℹ️ Durum", interactive=False)
            gallery = gr.Gallery(label="🖼️ Galeri", columns=3, rows=1, height=300)

    generate_btn.click(
        fn=generate_and_save,
        inputs=[init_image, prompt, mode, style, strength, guidance, gallery_state],
        outputs=[output_image, status, gallery]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
