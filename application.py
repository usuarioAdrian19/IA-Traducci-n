#!/usr/bin/python3

from flask import Flask, request, jsonify
import boto3
import os
from dotenv import load_dotenv

import aws_rekognition
import text_formatter
import google.generativeai as genai

# Load env variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)


# Get env variables
accessKeyId = os.environ.get('ACCESS_KEY_ID')
secretKey = os.environ.get('ACCESS_SECRET_KEY')
bucket_source = os.environ.get('BUCKET_SOURCE')
bucket_dest = os.environ.get('BUCKET_DEST')
google_api_key = os.environ.get('GOOGLE_API_KEY')
region = os.environ.get('REGION', 'eu-west-2')

# Create Flask application
application = Flask(__name__)

# Configurar Gemini
if google_api_key:
    genai.configure(api_key=google_api_key)

# Create the s3 service and assign credentials
s3 = boto3.Session(
    aws_access_key_id=accessKeyId,
    aws_secret_access_key=secretKey,
    region_name=region
).resource('s3')
    
def call_llm_translate(text):
    try:
        if not google_api_key:
            return "Error: No se ha configurado la API Key de Google."
        
        model = genai.GenerativeModel('models/gemini-2.5-pro')
        
        prompt = f"""
        Actúa como un traductor profesional. 
        Traduce el siguiente texto al español de manera natural y coherente.
        Si el texto ya está en español, corrígelo o mejóralo.

        Texto original:
        {text}
        """
        
        response = model.generate_content(prompt)
        return response.output_text 

    except Exception as e:
        return f"Error en LLM: {str(e)}"



# api/analyze endpoint
@application.route('/api/analyze', methods=['POST'])
def analyzeImage():
    response_data = {}
    status_code = 200

    try:
        data = request.get_json()
        
        if not data or 'key' not in data:
            return jsonify({"error": "No se recibió la clave 'key'"}), 400
            
        key = data['key']
        
        aws_response = aws_rekognition.detect_text_in_image(bucket_source, key)
        clean_text = text_formatter.extract_lines(aws_response)
        
        print("Traduciendo texto")
        translated_text = call_llm_translate(clean_text)
        
        response_data = {
            "status": "success",
            "extracted_text": clean_text, 
            "llm_analysis": translated_text, 
            "s3_location": f"s3://{bucket_source}/{key}"
        }
        
    except Exception as error:
        print(error)
        response_data = {"error": str(error)}
        status_code = 500

    return jsonify(response_data), status_code

# Ejecutar la aplicación
if __name__ == "__main__":
    application.run(debug=True, port=5000)