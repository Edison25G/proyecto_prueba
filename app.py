import requests
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://Edison:Contrasenia_1234!@localhost/clima_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Clima(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ciudad = db.Column(db.String(100))
    temperatura = db.Column(db.Float)
    sensacion_termica = db.Column(db.Float)
    humedad = db.Column(db.Integer)
    descripcion = db.Column(db.String(100))
    fecha_consulta = db.Column(db.DateTime)

first_request_done = False

@app.before_request
def create_tables_once():
    global first_request_done
    if not first_request_done:
        db.create_all()
        first_request_done = True

def obtener_clima(ciudad, api_key):
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': ciudad,
        'appid': api_key,
        'units': 'metric',
        'lang': 'es'
    }
    try:
        respuesta = requests.get(url, params=params)
        respuesta.raise_for_status()
        datos = respuesta.json()
        clima = {
            'ciudad': ciudad,
            'temperatura': datos['main']['temp'],
            'sensacion_termica': datos['main']['feels_like'],
            'humedad': datos['main']['humidity'],
            'descripcion': datos['weather'][0]['description'],
            'fecha_consulta': datetime.now()
        }
        return clima
    except requests.RequestException as e:
        print(f"Error al obtener datos para {ciudad}: {e}")
        return None

@app.route('/')
def index():
    api_key = 'ee83b60944a07ceca0db4649ffa11ea6'  # Pon aquí tu clave real
    resultados = Clima.query.order_by(Clima.fecha_consulta.desc()).all()
    return render_template('index.html', resultados=resultados)

@app.route('/actualizar')
def actualizar():
    api_key = 'ee83b60944a07ceca0db4649ffa11ea6'  # Pon aquí tu clave real
    ciudades = ['Quito', 'Guayaquil', 'Cuenca', 'Loja', 'Ambato']

    try:
        Clima.query.delete()
        db.session.commit()

        for ciudad in ciudades:
            clima = obtener_clima(ciudad, api_key)
            if clima:
                registro = Clima(
                    ciudad=clima['ciudad'],
                    temperatura=clima['temperatura'],
                    sensacion_termica=clima['sensacion_termica'],
                    humedad=clima['humedad'],
                    descripcion=clima['descripcion'],
                    fecha_consulta=clima['fecha_consulta']
                )
                db.session.add(registro)
        db.session.commit()
        flash('Datos actualizados correctamente.', 'success')
    except Exception as e:
        flash(f'Error al actualizar datos: {e}', 'danger')

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
