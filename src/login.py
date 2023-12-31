from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, session, abort
import hashlib
from __main__ import app
from .models import db, Preceptor, Asistencia, Curso, Estudiante, Padre

def check_pass(password):
    return hashlib.md5(bytes(password, encoding='utf-8')).hexdigest()

def authenticate(email, password, user_type):
    user = None
    if user_type == 'preceptor':
        user = db.session.query(Preceptor).filter_by(correo=email).first()
    elif user_type == 'padre':
        user = db.session.query(Padre).filter_by(correo=email).first()
    if user and user.clave == check_pass(password):
        return user
    return None

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        user = authenticate(email, password, user_type)
        if user:
            session['user_id'] = user.id
            session['user_type'] = user_type
            return redirect(url_for('home'))
        else:
            return "Credenciales incorrectas"
    return render_template('login.html')

@app.route('/home')
def home():
    tipo_usuario = session.get('user_type', None)
    if not tipo_usuario:
        return redirect(url_for('login'))
    preceptor_actual = None
    cursos = None
    if tipo_usuario == 'preceptor':
        preceptor_actual = obtener_id_preceptor()
        cursos = preceptor_actual.cursos
    return render_template('home.html', tipo_usuario=tipo_usuario, cursos=cursos)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_type', None)
    return redirect(url_for('login'))

def obtener_id_preceptor():
    if 'user_id' not in session:
        return None
    return Preceptor.query.get(session['user_id'])
