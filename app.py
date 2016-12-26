 # -*- coding: utf-8 -*-
import sqlite3
import os
import requests
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

# конфигурация
DATABASE = '/tmp/rm.db'
DEBUG = True
SECRET_KEY = 'key new'
USERNAME = 'admin'
PASSWORD = 'pass'

# создаём наше маленькое приложение :)
app = Flask(__name__)
app.config.from_object(__name__)

# Загружаем конфиг по умолчанию и переопределяем в конфигурации часть
# значений через переменную окружения
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'rm.db'),
    DEBUG=True,
    SECRET_KEY='key new',
    USERNAME='admin',
    PASSWORD='pass'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    """Соединяет с указанной базой данных."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv
    
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
    
def get_db():
    """Если ещё нет соединения с базой данных, открыть новое - для
    текущего контекста приложения
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db
    
@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
        
@app.route('/')
def index():
    db = get_db()
    cur = db.execute('select id, url, times, status from reslist order by id desc')
    reslist = cur.fetchall()
    
    return render_template('index.html', reslist=reslist)
    
@app.route('/add_url', methods=['POST'])
def add_url():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into reslist (url, times) values (?, ?)',
                [request.form['url'], request.form['times']])
    db.commit()
    flash('New url was successfully added!')
    return redirect(url_for('index'))
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)
    
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))

@app.route('/update', methods=['POST'])    
def url_ping(url=None):
    if not session.get('logged_in'):
        abort(401)
    db = get_db()    
    cur = db.execute('select id, url, times, status from reslist order by id desc')
    resl = cur.fetchall()
    try:        
        for i in resl:                       
            res = requests.get(i[1], timeout=3)            
            #if res.status_code==200:
            #    cc='OK'
            #    flash(2)
            #else:
            #    cc='NO'   
            cc=res.status_code
            db.execute("UPDATE reslist SET status=%s WHERE id=%s" % (cc, i[0]))            
            db.commit()
    except:
        pass   
    flash('Successfully update!')
    return redirect(url_for('index'))
    
#@app.route('/del_url', methods=['POST'])
#def del_url():
#    if not session.get('logged_in'):
#        abort(401)
#    db = get_db()
#    db.execute('insert into reslist (url, times) values (?, ?)',
#                [request.form['url'], request.form['times']])
#    db.commit()
#    flash('New url was successfully added')
#    return redirect(url_for('index'))
    
if __name__ == '__main__':
    app.run('127.0.0.1', 8100, debug=True)
#    app.run()