from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
CORS(app)  # Habilita CORS para permitir peticiones desde el frontend

# Configuración de la conexión a MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Cambia si usas una contraseña
    'database': 'escuela'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        print("Conexión a MySQL establecida")  # Mensaje de confirmación
        return connection
    except Error as e:
        print(f"Error de conexión: {e}")
        return None

# Ruta principal para mostrar el HTML
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para obtener todos los alumnos
@app.route('/alumnos', methods=['GET'])
def get_alumnos():
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM alumnos")
    alumnos = cursor.fetchall()
    connection.close()
    return jsonify(alumnos)

# Ruta para agregar un nuevo alumno (POST)
@app.route('/alumnos', methods=['POST'])
def add_alumno():
    new_alumno = request.json
    print("Datos recibidos para agregar:", new_alumno)  # Imprime los datos recibidos para depurar

    # Validación de datos antes de insertar
    if not new_alumno or 'name' not in new_alumno or 'Carrera' not in new_alumno or 'Edad' not in new_alumno:
        return jsonify({"error": "Datos incompletos"}), 400

    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    cursor = connection.cursor()
    
    try:
        cursor.execute("INSERT INTO alumnos (name, carrera, edad) VALUES (%s, %s, %s)", 
                       (new_alumno['name'], new_alumno['Carrera'], new_alumno['Edad']))
        connection.commit()
        
        new_alumno_id = cursor.lastrowid
        connection.close()
        
        new_alumno['id'] = new_alumno_id
        return jsonify({"alumno": new_alumno, "message": "Nuevo alumno agregado correctamente"}), 201
    except Error as e:
        connection.rollback()
        print(f"Error al agregar alumno: {e}")
        return jsonify({"error": "Error al agregar alumno"}), 500

# Ruta para actualizar un alumno (PUT)
@app.route('/alumnos/<int:id_item>', methods=['PUT'])
def update_alumno(id_item):
    updated_data = request.json
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM alumnos WHERE id = %s", (id_item,))
    alumno = cursor.fetchone()
    
    if alumno:
        cursor.execute("UPDATE alumnos SET name = %s, carrera = %s, edad = %s WHERE id = %s",
                       (updated_data['name'], updated_data['Carrera'], updated_data['Edad'], id_item))
        connection.commit()
        connection.close()
        return jsonify(updated_data)
    else:
        connection.close()
        return jsonify({"error": "Alumno no encontrado"}), 404

# Ruta para eliminar un alumno (DELETE)
@app.route('/alumnos/<int:id_item>', methods=['DELETE'])
def delete_alumno(id_item):
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM alumnos WHERE id = %s", (id_item,))
    alumno = cursor.fetchone()

    if alumno:
        cursor.execute("DELETE FROM alumnos WHERE id = %s", (id_item,))
        connection.commit()
        connection.close()
        return jsonify({"message": "Alumno eliminado"}), 200
    else:
        connection.close()
        return jsonify({"error": "Alumno no encontrado"}), 404

if __name__ == '__main__':
    app.run(debug=True)
