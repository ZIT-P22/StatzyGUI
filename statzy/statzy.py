from flask import Flask, render_template, request
import psycopg2

statzy = Flask(__name__)


@statzy.route('/')
def index():
    title = 'Statzy'
    return render_template('login.html', title=title)


@statzy.route('/fachverfahren')
def fachverfahren():
    tag = 'T1'
    try:
        print("Test 0")
        cursor = conn.cursor()
        print("Test 1")
        query = "SELECT name, verf_id, tag, vewendungszweck, laufzeitverfahren, auftraggeber, verf_betreuung, kundenmanagement, fachadministation FROM fachverfahren WHERE tag = '" + tag + "' ORDER BY name "
        #query = "SELECT tag FROM fachverfahren WHERE tag = '" + tag + "' ORDER BY name "
        print("Test 2")
        cursor.execute(query)
        print("Test 3")
        results = cursor.fetchall()
        print(results)

        # Unpacking der Werte in Variablen
        name, verf_id, tag, vewendungszweck, laufzeitverfahren, auftraggeber, verf_betreuung, kundenmanagement, fachadministation = results[0]

        return render_template('fachverfahren.html', name=name, verf_id=verf_id, tag=tag, vewendungszweck=vewendungszweck, laufzeitverfahren=laufzeitverfahren, auftraggeber=auftraggeber, verf_betreuung=verf_betreuung, kundenmanagement=kundenmanagement, fachadministation=fachadministation)
        #return results
    except:
        print("Test 4")
        return 'Fehler'


@statzy.route('/datenbanken')
def datenbanken():
    return render_template('datenbanken.html')


@statzy.route('/server')
def server():
    return render_template('server.html')


@statzy.route('/komponenteServer')
def komponenteServer():
    return render_template('komponenteServer.html')


@statzy.route('/login', methods=['POST'])
def login():
    global conn
    username = request.form['username']
    password = request.form['password']
    try:
        conn = psycopg2.connect(
            dbname='statzy',
            user='postgres',
            password='postgres',
            host='localhost',
            port='5432'
        )
        cursor = conn.cursor()

        # Get the list of tables in the database
        cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
        tables = [table[0] for table in cursor.fetchall()]

        # Render the template with the dropdown menu
        return render_template('index.html', tables=tables)
    except:
        return 'Database connection failed!'


@statzy.route('/query', methods=['POST'])
def query():
    table_name = request.form['table']
    try:
        cursor = conn.cursor()

        # Execute the SELECT * query on the selected table
        cursor.execute(
            "SELECT * FROM {table_name}")
        results = cursor.fetchall()

        # Render the template with the query results

        return render_template('query.html', table_name=table_name, results=results)
    except:
        return 'Database connection failed!'


if __name__ == '__main__':
    statzy.run(debug=True)
