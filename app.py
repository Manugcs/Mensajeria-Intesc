import os # Esta librería es para el .env y sirve para recuperar los datos que tiene ese archivo encriptados
import requests
import hmac
import hashlib
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Así es como flask actúa como el núcleo de mi servidor (inicializando una instancia de Flask)
app = Flask(__name__)


# Configurar las credenciales de WhatsApp API de Meta
load_dotenv()
WHATSAPP_API_URL = os.getenv("WHATSAPP_API")  #'https://graph.facebook.com/v21.0/WHATSAPP_NUMBER_ID/messages' 
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")

if not WHATSAPP_API_URL or not WHATSAPP_TOKEN:
    raise ValueError("Faltan variables necesarias en el archivo .env")

print(f"WhatsApp API URL: {WHATSAPP_API_URL}")
print(f"WhatsApp Token: {WHATSAPP_TOKEN}")

#Enviamos el mensaje de Whats usando las plantillas
def send_whatsapp_template(phone_number, customer_name):
    if not WHATSAPP_API_URL:
        raise ValueError("La variable WHATSAPP_API_URL no está configurada. Revisar archivo .env")
    
    #Aseguramos el formateo del número para enviar mensaje
    if len(phone_number) == 10 and phone_number.isdigit():
        phone_number = f"52{phone_number}"

    headers = {
        'Authorization': f'Bearer {WHATSAPP_TOKEN}',
        'Content-Type': 'application/json'
    }
    payload = {
        'messaging_product': 'whatsapp',
        'to': phone_number,
        'type': 'template',
        'template': {
            'name': 'agradecimiento',
            'language':{
                'code' : 'es_MX'
            },
            'components' : [
                {
                    'type': 'body',
                    'parameters': [
                        {
                            'type': 'text',
                            'text': customer_name
                        }
                    ]
                }
            ]
        }
    }
    print(f"Using WHATSAPP_API_URL: {WHATSAPP_API_URL}")
    print(f"ENVIANDO MENSAJE A {phone_number} USANDO LA PLANTILLA...")
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.text}")
    return response.json()

#Definimos una ruta lo que significa que el servidor espera solicitudes HTTP
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    # Imprime el cuerpo recibido
    print("JSON Payload:", data)

    # Extrae los datos necesarios
    billing_info = data.get('billing', {})
    customer_phone = billing_info.get('phone')
    customer_name = billing_info.get('first_name')

    print(f"Customer Phone: {customer_phone}")
    print(f"Customer Name: {customer_name}")

    if customer_phone and customer_name:
        send_whatsapp_template(customer_phone, customer_name)

    return jsonify({'status': 'success'}), 200



#Arranca el servidor en el puerto 5000 y estará escuchando en la dirección http://127.0.0.1:5000/ o sea mi máquina local
if __name__ == '__main__':
    app.run(port=5000, debug=True)
