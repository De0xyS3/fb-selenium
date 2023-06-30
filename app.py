import csv
from io import StringIO
import time
import random
import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import telegram
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Creación del bot de Telegram
bot = telegram.Bot(token="token")

progress = 0

async def run_script(username, password, url, comment, reaction):
    global progress
   # Configuración de Selenium
    driver = webdriver.Chrome('/snap/bin/chromium.chromedriver')
    chrome_options = Options()
    chrome_options.add_argument('--disable-notifications')
    driver.implicitly_wait(10)

    # Iniciar sesión en Facebook
    driver.get('https://www.facebook.com/')
    time.sleep(2)

    username_field = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div/div/div[2]/div/div[1]/form/div[1]/div[1]/input')
    password_field = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div/div/div[2]/div/div[1]/form/div[1]/div[2]/div/input')

    username_field.send_keys(username)
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)
    time.sleep(5)

    # Navegar a la URL del post
    driver.get(url)
    time.sleep(2)

    # Manejar la reacción seleccionada
    if reaction == "Me gusta":
        boton_me_gusta = driver.find_element(By.CSS_SELECTOR, "a._15ko._77li.touchable")
        boton_me_gusta.click()
    elif reaction == "Me encanta":
        boton_me_encanta = driver.find_element(By.CSS_SELECTOR, "_15ko _77li _77la _77ld touchable")
        boton_me_encanta.click()
    time.sleep(1)

    # Encontrar el elemento del textarea para el comentario
    comentario_textarea = driver.find_element(By.CSS_SELECTOR, "textarea._uwx.mentions-input")

   # Insertar el comentario correspondiente
    if comment == "Opción aleatoria":
        comentarios = [
            "¿Me puedes contar más sobre eso?",
            "Eso suena interesante. ¿Podrías explicarlo con más detalle?",
            "Me encantaría saber cómo llegaste a esa conclusión.",
            "Parece que tienes mucho conocimiento en este tema. ¿Podrías compartir más al respecto?",
            "¿Qué te inspiró a trabajar en esto?",
            "Me gustaría saber más sobre tu experiencia en esta área.",
            "¿Hay algún recurso que recomendarías para aprender más sobre esto?",
            "Estoy intrigada. ¿Cómo llegaste a esa idea?",
            "Me gustaría escuchar tu perspectiva sobre este asunto.",
            "¿Hay algún proyecto en el que estés trabajando actualmente que te emocione?"
        ]
        comentario_aleatorio = random.choice(comentarios)
        comentario_textarea.send_keys(comentario_aleatorio)
    else:
        comentario_textarea.send_keys(comment)
    time.sleep(2)

    # Encontrar el botón de publicar comentario
    boton_publicar = driver.find_element(By.CSS_SELECTOR, "button._54k8._52jg._56bs._26vk._3lmf._3fyi._56bv._653w")
    boton_publicar.click()
    time.sleep(5)

    # Enviar mensaje de confirmación a Telegram
    await bot.send_message(chat_id="ID", text="Comentario y reacción realizados correctamente")

    driver.close()

# Rutas de la aplicación Flask
@app.route('/', methods=['GET', 'POST'])
def index():
    global progress

    reactions = ['Me gusta', 'Me encanta']
    congratulations = [
        'Obtuvo un buen rendimiento escolar, ¡Felicitaciones!',
        'Demostró interés por obtener buenas calificaciones. ¡Excelente trabajo!'
    ]

    if request.method == 'POST':
        if 'csvfile' in request.files and request.files['csvfile']:
            # Leer el contenido del archivo CSV
            csvfile = request.files['csvfile']
            csv_data = csvfile.read().decode('utf-8')

            # Procesar cada línea del archivo CSV
            csv_reader = csv.reader(StringIO(csv_data), delimiter=';')

            # Obtener los datos del formulario
            url = request.form['url']
            comment = request.form['comment']
            reaction = request.form['reaction']

            # Ejecutar el script de Selenium para cada usuario en el archivo CSV
            for row in csv_reader:
                if len(row) >= 2:
                    username, password = row[0], row[1]
                    progress = 0

                    # Ejecutar el script de Selenium en segundo plano
                    asyncio.run(run_script(username, password, url, comment, reaction))

        else:
            # Obtener los datos del formulario
            username = request.form['username']
            password = request.form['password']
            url = request.form['url']
            comment = request.form['comment']
            reaction = request.form['reaction']

            progress = 0

            # Ejecutar el script de Selenium en segundo plano
            asyncio.run(run_script(username, password, url, comment, reaction))


    return render_template('index.html', reactions=reactions, congratulations=congratulations)

@app.route('/progress')
def get_progress():
    global progress

    return jsonify({'progress': progress})

if __name__ == '__main__':
    app.run()
