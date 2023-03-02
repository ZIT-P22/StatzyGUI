from flask import Flask, render_template, request, Response
import psycopg2


statzy = Flask(__name__)


@statzy.route('/')
def index():
    title = 'Statzy'
    return render_template('index.html', title=title)


@statzy.route('/fachverfahren')
def fachverfahren():
    return render_template('fachverfahren.html')


@statzy.route('/datenbanken')
def datenbanken():
    return render_template('datenbanken.html')


@statzy.route('/server')
def server():
    return render_template('server.html')


@statzy.route('/stammdaten')
def stammdaten():
    return render_template('stammdaten.html')


@statzy.route('/komponenteServer')
def komponenteServer():
    return render_template('komponenteServer.html')


@statzy.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    try:
        conn = psycopg2.connect(
            dbname='stratzy',
            user=username,
            password=password,
            host='localhost',
            port='5432'
        )
        # database connection is successful
        cursor = conn.cursor()

        # execute SQL queries and handle database operations here
        # ...

        cursor.close()
        conn.close()
        return 'Database connection successful!'
    except:
        # database connection failed
        return 'Database connection failed!'


if __name__ == '__main__':
    statzy.run()
