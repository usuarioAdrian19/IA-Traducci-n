import gradio as gr
import boto3
import requests
import os
import time
from dotenv import load_dotenv
from PIL import Image
import io

load_dotenv()

# Configuración AWS
ACCESS_KEY = os.getenv('ACCESS_KEY_ID')
SECRET_KEY = os.getenv('ACCESS_SECRET_KEY')
BUCKET_SOURCE = os.getenv('BUCKET_SOURCE')
REGION = os.getenv('REGION')
FLASK_URL = "http://127.0.0.1:5000/api/analyze"

s3_client = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=REGION
)

def procesar_traduccion(imagen):
    if imagen is None:
        return None, None, "Sube una imagen"

    try:
        nombre_archivo = f"foto_translate_{int(time.time())}.jpg"
        buffer = io.BytesIO()
        imagen.save(buffer, format="JPEG")
        buffer.seek(0)

        s3_client.upload_fileobj(buffer, BUCKET_SOURCE, nombre_archivo)
        
        payload = {"key": nombre_archivo}
        response = requests.post(FLASK_URL, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('extracted_text'), data.get('llm_analysis'), "Texto traducido"
        else:
            return None, None, f"Error del servidor: {response.status_code}"

    except Exception as e:
        return None, None, f"Error: {str(e)}"

with gr.Blocks() as demo:
    gr.Markdown("Traductor de Imagenes")
    gr.Markdown("Sube una imagen en otro idioma, y se traducira al español ")
    
    with gr.Row():
        with gr.Column():
            input_img = gr.Image(type="pil", label="Imagen Original")
            btn = gr.Button("Traducir al Español", variant="primary")
            status = gr.Textbox(label="Estado", interactive=False)
            
        with gr.Column():
            # Mostramos el texto original y la traducción
            text_original = gr.TextArea(label="Texto Original")
            text_translated = gr.TextArea(label="Texto Traducido")

    btn.click(fn=procesar_traduccion, inputs=input_img, outputs=[text_original, text_translated, status])

if __name__ == "__main__":
    demo.launch()