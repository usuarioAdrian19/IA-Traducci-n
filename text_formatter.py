def extract_lines(aws_response):
    """
    Recibe el JSON completo de AWS Rekognition.
    Filtra solo las líneas de texto detectadas (Type='LINE') 
    y las une en un solo string legible.
    """
    detected_text = []
    
    # La respuesta de Rekognition contiene una lista 'TextDetections'
    if 'TextDetections' in aws_response:
        for item in aws_response['TextDetections']:
            # Filtramos por 'LINE' para evitar palabras sueltas duplicadas
            if item['Type'] == 'LINE':
                detected_text.append(item['DetectedText'])
    
    full_text = "\n".join(detected_text)
    return full_text