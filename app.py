from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuración para conectar a MySQL con PyMySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://Edison:Contrasenia1234@localhost/mi_base_estudiantes'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Estudiante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

first_request_done = False

@app.before_request
def create_tables_once():
    global first_request_done
    if not first_request_done:
        db.create_all()
        first_request_done = True

@app.route('/')
def index():
    estudiantes = Estudiante.query.all()
    return render_template('index.html', estudiantes=estudiantes)

@app.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        nuevo = Estudiante(nombre=nombre, email=email)
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('crear.html')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    estudiante = Estudiante.query.get_or_404(id)
    if request.method == 'POST':
        estudiante.nombre = request.form['nombre']
        estudiante.email = request.form['email']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('editar.html', estudiante=estudiante)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    estudiante = Estudiante.query.get_or_404(id)
    db.session.delete(estudiante)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
