from flask import Flask, render_template, request, flash, redirect, url_for, session
from flaskext.mysql import MySQL
from flask_mysqldb import MySQL,MySQLdb
from flask import send_from_directory
from datetime import datetime
import bcrypt
import os


app = Flask(__name__)
app.secret_key = "login"
app.config['MYSQL_HOST'] = 'LAPTOP-GR13V90V'
app.config['MYSQL_USER'] = 'user'
app.config['MYSQL_PASSWORD'] = 'kyungshin1!'
app.config['MYSQL_DB'] = 'db_admin'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

CARPETA = os.path.join('uploads')
app.config['CARPETA'] = CARPETA

conn = MySQLdb.connect(host="172.30.63.177", user="user", password="kyungshin1!", db="db_admin")

#This is the index route where we are going to
#query on all our employee data
""" @app.route('/')
def Index():
    cur =  conn.cursor()
    cur.execute('SELECT * FROM activities')
    data = cur.fetchall()
    cur.close()
    return render_template('index.html', activities = data)
     """

@app.route('/')
def main():
    if 'name' in session:
        return render_template('/base.html')
    else:
        return render_template('/login.html')

@app.route('/inicio')
def inicio():

    if 'name' in session:
         cur =  conn.cursor()
         cur.execute('SELECT id_a, department, request, description, assign, status, date_format(datetime,"%e %M %Y %H:%i:%s"),incidencia FROM register_activity;')
        
         data = cur.fetchall()
         cur.close()
         return render_template('/tabla.html', register_activity = data)
    else:
        return render_template('/login.html')


##################### INGRESAR #################################


@app.route('/ingresar',methods=["GET","POST"])
def ingresar():
    if request.method == 'POST':
     
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM users WHERE email=%s",(email,))
        user = curl.fetchone()
        curl.close()

        if (user != None):
            if bcrypt.hashpw(password, user["password"].encode('utf-8')) == user["password"].encode('utf-8'):
                session['name'] = user['name']
                session['email'] = user['email']
                return redirect(url_for('inicio'))
               
            else:
                flash("El password no es correcto")
                return render_template('/login.html')
        else:
                flash("El usuario no existe")
                return render_template('/login.html')
    else:
        return render_template("login.html")


##################### REGISTRAR #################################
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("/register.html")
    else:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email, password) VALUES (%s,%s,%s)",(name,email,hash_password,))
        mysql.connection.commit()
        session['name'] = request.form['name']
        session['email'] = request.form['email']
        return redirect(url_for('inicio'))

##################### SALIR #################################
@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.clear()
    return render_template('/login.html')

##################### INSERTAR #################################
@app.route('/insert', methods = ['POST'])
def insert():

    if request.method == 'POST':

        department = request.form['department']
        solicita = request.form['solicita']
        descripcion = request.form['descripcion']
        asignante = request.form['asignante']
        status = request.form['status']
        incidencia = request.form['incidencia']

        cur =  conn.cursor()
        cur.execute("INSERT INTO register_activity (department, request, description, assign, status, incidencia) VALUES (%s,%s,%s,%s,%s,%s)", (department, solicita, descripcion, asignante, status,incidencia))
        conn.commit()

        flash("Activity Inserted Successfully")

        return redirect(url_for('inicio'))




##################### UPDATE #################################
@app.route('/update', methods = ['GET', 'POST'])
def update():

    if request.method == 'POST':
        
        id_a = request.form['id']
        department = request.form['department']
        solicita = request.form['solicita']
        descripcion = request.form['descripcion']
        asignante = request.form['asignante']
        status = request.form['status']
        incidencia = request.form['incidencia']

        cur =  conn.cursor()
        cur.execute("""UPDATE register_activity
                                    SET  department = %s,
                                          request = %s,
                                          description = %s,
                                          assign = %s,
                                          status = %s,
                                          incidencia = %s
                                           WHERE id_a = %s""", (department, solicita, descripcion, asignante, status,incidencia, id_a))
        
        conn.commit()
        flash("Activity Updated Successfully")
        return redirect(url_for('inicio'))




#####################------------------------------------ RUTAS---------------------------------------------------- #################################
@app.route('/conocimiento')
def base():
    if 'name' in session:
         cur =  conn.cursor()
         cur.execute('SELECT * FROM base')
         data = cur.fetchall()
         cur.close()
         return render_template('/base_conocimiento.html', base = data)
    else:
        return render_template('/login.html')


@app.route('/ver/<id>')
def ver(id):
    if 'name' in session:
        cur =  conn.cursor()
        cur.execute('SELECT * FROM base WHERE id_con = %s', id)
        data = cur.fetchall()
        cur.close()
        return render_template('/mostrar.html', base = data)
    else:
        return render_template('/login.html')


@app.route('/mostrar')
def mostrar():

    if 'name' in session:
        return render_template('/mostrar.html')
    else:
        return render_template('/login.html')

    

##################### INSERTAR BASE DE CONOCIMIENTOS #################################
@app.route('/insertar', methods = ['POST'])
def insertar():

    if request.method == 'POST':

        tema = request.form['tema']
        breve = request.form['breve']
        descripcion = request.form['descripcion']
        solucion = request.form['solucion']
        imagen = request.files['imagen']

        now = datetime.now()
        tiempo = now.strftime("%Y%H%M%S")

        if imagen.filename != '':
            nuevoNombreFoto = tiempo+imagen.filename
            imagen.save("uploads/"+nuevoNombreFoto)

        cur =  conn.cursor()
        cur.execute("INSERT INTO base (tema, breve_descripcion, descripcion_com, solucion, imagen) VALUES (%s,%s,%s,%s,%s)", (tema, breve, descripcion, solucion, nuevoNombreFoto))
       
        conn.commit()

        flash("Knowledge Inserted Successfully")

    return redirect(url_for('base'))


    ##################### EDITAR BASE DE CONOCIMIENTOS #################################
@app.route('/editar', methods = ['GET', 'POST'])
def editar():

    if request.method == 'POST':

        id_con = request.form['id']
        tema = request.form['tema']
        breve = request.form['breve']
        descripcion = request.form['descripcion']
        solucion = request.form['solucion']
        imagen = request.files['imagen']

        cur =  conn.cursor()
       
      
        now = datetime.now()
        tiempo = now.strftime("%Y%H%M%S")

        if imagen.filename != '':

            nuevoNombreFoto = tiempo  +imagen.filename
            imagen.save("uploads/"+nuevoNombreFoto)

        
            cur.execute("SELECT imagen FROM base where id_con =%s", id_con)
       

            cur.execute("UPDATE base SET imagen = %s WHERE id_con=%s",(nuevoNombreFoto,id_con))

            conn.commit()


        cur.execute("""UPDATE base
                                    SET  tema = %s,
                                          breve_descripcion = %s,
                                          descripcion_com = %s,
                                          solucion = %s
                                           WHERE id_con = %s""", (tema, breve, descripcion, solucion, id_con))
       
        conn.commit()


        flash("Knowledge Updated Successfully")

    return redirect(url_for('base'))
    

#DAshboard
@app.route('/dashboard')
def dash():

    if 'name' in session:
        return render_template('/dashboard.html')
    else:
        return render_template('/login.html')


@app.route('/uploads/<imagen>')
def uploads(imagen):

    return send_from_directory(app.config['CARPETA'], imagen)


if __name__ == "__main__":
    app.run(debug=True)