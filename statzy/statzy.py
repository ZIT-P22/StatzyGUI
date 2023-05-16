from flask import Flask, render_template, request, redirect, url_for, session, g
import psycopg2
from psycopg2 import pool
import secrets

statzy = Flask(__name__)
statzy.secret_key = secrets.token_hex(16)


#! def zone start

# Create a connection pool
connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=20,
    dbname='statzy',
    user='postgres',
    password='postgres',
    host='10.128.201.123',
    port='5432'
)


def get_db():
    if 'db' not in g:
        g.db = connection_pool.getconn()
    return g.db


@statzy.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        connection_pool.putconn(db)  # Release the connection back to the pool


def db_execute(query, *args):
    cursor = get_cursor()
    cursor.execute(query, *args)
    return cursor.fetchall()


def personValidate(person_id):
    cursor = get_cursor()
    query = "SELECT count(*) FROM person WHERE person_id = '" + person_id + "'"
    cursor.execute(query)
    results = cursor.fetchall()

    if results[0][0] == 1:
        return True
    else:
        return False

# ? funktion die in der person Datenbank die Id sucht un den dazugehörigen Namen zurückgibt


def personIdToName(person_id):
    query = "SELECT name FROM person WHERE person_id = '" + \
        str(person_id) + "'"
    results = db_execute(query)
    return results[0][0]


def get_cursor():
    if 'cursor' not in g:
        g.cursor = get_db().cursor()
    return g.cursor


#! def zone end


@statzy.teardown_appcontext
def close_db(e=None):
    cursor = g.pop('cursor', None)
    db = g.pop('db', None)

    if cursor is not None:
        cursor.close()
    if db is not None:
        db.close()


@statzy.route('/')
def index():
    title = 'Statzy'
    return render_template('login.html', title=title)


@statzy.route('/start')
def start():
    try:
        query = "SELECT name, verf_id, tag FROM fachverfahren ORDER BY name"
        fachverfahren_data = db_execute(query)

        print(fachverfahren_data)
        return render_template('index.html', fachverfahren_data=fachverfahren_data)

    except Exception as e:
        # print("Error:", e)
        return 'Fehler AAAAAAAAAAHHHHHHHHHHHHHHHH!!!!!'


@statzy.route('/person')
def person():
    return render_template('person.html')


@statzy.route('/personSuche')
def personSuche():
    return render_template('personSuche.html', warning=0)


@statzy.route('/personAnsehen', methods=['GET', 'POST'])
def personAnsehen():
    if request.method == 'POST':
        name = request.form['name']
        try:
            query = "SELECT name, telefonnummer, dez, vornam, person_id, zeitpunkt_ins, user_ins, zeitpunkt_upd, user_upd FROM person WHERE name ~* '" + name + "' ORDER BY name "
            db_execute(query)
            if not results:
                return render_template('person.html', warning=1, name=name)
            name, telefonnummer, dez, vornam, person_id, zeitpunkt_ins, user_ins, zeitpunkt_upd, user_upd = results[
                0]
            return render_template('personAnsehen.html', name=name, telefonnummer=telefonnummer, dez=dez, vornam=vornam, person_id=person_id, zeitpunkt_ins=zeitpunkt_ins, user_ins=user_ins, zeitpunkt_upd=zeitpunkt_upd, user_upd=user_upd)
        except Exception as e:
            return 'Fehler', e
    else:
        name = request.args.get('name')
        try:
            query = "SELECT name, telefonnummer, dez, vornam, person_id, zeitpunkt_ins, user_ins, zeitpunkt_upd, user_upd FROM person WHERE name ~* '" + name + "' ORDER BY name"
            results = db_execute(query, (name,))
            if not results:
                return render_template('person.html', warning=1, name=name)
            name, telefonnummer, dez, vornam, person_id, zeitpunkt_ins, user_ins, zeitpunkt_upd, user_upd = results[
                0]
            return render_template('personAnsehen.html', name=name, telefonnummer=telefonnummer, dez=dez, vornam=vornam, person_id=person_id, zeitpunkt_ins=zeitpunkt_ins, user_ins=user_ins, zeitpunkt_upd=zeitpunkt_upd, user_upd=user_upd)
        except Exception as e:
            return 'Fehler', e


@statzy.route('/personEditieren', methods=['POST'])
def personEditieren():
    name = request.form['name']
    try:
        query = "SELECT name, telefonnummer, dez, vornam, person_id, zeitpunkt_ins, user_ins, zeitpunkt_upd, user_upd FROM person WHERE name ~* '" + name + "' ORDER BY name"
        results = db_execute(query)
        name, telefonnummer, dez, vornam, person_id, zeitpunkt_ins, user_ins, zeitpunkt_upd, user_upd = results[
            0]
        return render_template('personEditieren.html', name=name, telefonnummer=telefonnummer, dez=dez, vornam=vornam, person_id=person_id, zeitpunkt_ins=zeitpunkt_ins, user_ins=user_ins, zeitpunkt_upd=zeitpunkt_upd, user_upd=user_upd)
    except:
        return 'Fehler'


@statzy.route('/personUpdate', methods=['POST'])
def personUpdate():
    name = request.form['name']
    telefonnummer = request.form['telefonnummer']
    dez = request.form['dez']
    vornam = request.form['vornam']
    zeitpunkt_ins = request.form['zeitpunkt_ins']
    user_ins = request.form['user_ins']
    zeitpunkt_upd = request.form['zeitpunkt_upd']
    user_upd = request.form['user_upd']

    try:
        cursor = get_cursor()
        query = """UPDATE person SET name=%s, telefonnummer=%s, dez=%s, vornam=%s, zeitpunkt_ins=%s, user_ins=%s, 
                zeitpunkt_upd=%s, user_upd=%s WHERE name=%s"""
        cursor.execute(query, (name, telefonnummer, dez, vornam, zeitpunkt_ins,
                       user_ins, zeitpunkt_upd, user_upd, name))
        get_db().commit()
        return redirect(url_for('personAnsehen', name=name))
    except Exception as e:
        return 'Fehler: ' + str(e)


@statzy.route('/fachverfahrenSuche')
def fachverfahrenSuche():
    return render_template('fachverfahrenSuche.html', warning=0)


@statzy.route('/fachverfahrenAnsehen', methods=['GET', 'POST'])
def fachverfahrenAnsehen():
    # ? Wenn die Methode POST ist, wird der Tag aus dem Formular genommen
    if request.method == 'POST':
        tag = request.form['tag']
        try:
            query = "SELECT name, verf_id, tag, vewendungszweck, laufzeitverfahren, auftraggeber, verf_betreuung, kundenmanagement, fachadministration FROM fachverfahren WHERE tag ~* '" + tag + "' ORDER BY name "
            results = db_execute(query)

            if not results:
                return render_template('fachverfahrenSuche.html', warning=1, tag=tag)

            name, verf_id, tag, vewendungszweck, laufzeitverfahren, auftraggeber, verf_betreuung, kundenmanagement, fachadministration = results[
                0]

            auftraggeber = personIdToName(auftraggeber)
            verf_betreuung = personIdToName(verf_betreuung)
            kundenmanagement = personIdToName(kundenmanagement)
            fachadministration = personIdToName(fachadministration)

            return render_template('fachverfahrenAnsehen.html', name=name, verf_id=verf_id, tag=tag, vewendungszweck=vewendungszweck, laufzeitverfahren=laufzeitverfahren, auftraggeber=auftraggeber, verf_betreuung=verf_betreuung, kundenmanagement=kundenmanagement, fachadministration=fachadministration)
        except Exception as e:
            return 'Fehler' + str(e)
    # ? Wenn die Methode GET ist, wird der Tag aus der URL genommen
    else:
        tag = request.args.get('tag')
        try:
            query = "SELECT name, verf_id, tag, vewendungszweck, laufzeitverfahren, auftraggeber, verf_betreuung, kundenmanagement, fachadministration FROM fachverfahren WHERE tag ~* %s ORDER BY name"
            results = db_execute(query, (tag,))

            if not results:
                return render_template('fachverfahrenSuche.html', warning=1, tag=tag)

            name, verf_id, tag, vewendungszweck, laufzeitverfahren, auftraggeber, verf_betreuung, kundenmanagement, fachadministration = results[
                0]

            auftraggeber = personIdToName(auftraggeber)
            verf_betreuung = personIdToName(verf_betreuung)
            kundenmanagement = personIdToName(kundenmanagement)
            fachadministration = personIdToName(fachadministration)

            return render_template('fachverfahrenAnsehen.html', name=name, verf_id=verf_id, tag=tag, vewendungszweck=vewendungszweck, laufzeitverfahren=laufzeitverfahren, auftraggeber=auftraggeber, verf_betreuung=verf_betreuung, kundenmanagement=kundenmanagement, fachadministration=fachadministration)
        except:
            return 'Fehler'


@statzy.route('/fachverfahrenEditieren', methods=['POST'])
def fachverfahrenEditieren():
    tag = request.form['tag']
    try:
        query = "SELECT name, verf_id, tag, vewendungszweck, laufzeitverfahren, auftraggeber, verf_betreuung, kundenmanagement, fachadministration FROM fachverfahren WHERE tag ~* '" + tag + "' ORDER BY name "
        results = db_execute(query)

        name, verf_id, tag, vewendungszweck, laufzeitverfahren, auftraggeber, verf_betreuung, kundenmanagement, fachadministration = results[
            0]
        return render_template('fachverfahrenEditieren.html', name=name, verf_id=verf_id, tag=tag, vewendungszweck=vewendungszweck, laufzeitverfahren=laufzeitverfahren, auftraggeber=auftraggeber, verf_betreuung=verf_betreuung, kundenmanagement=kundenmanagement, fachadministration=fachadministration)
    except:
        return 'Fehler'


@statzy.route('/fachverfahrenUpdate', methods=['POST'])
def fachverfahrenUpdate():
    name = request.form['it-verfahren-namen']
    verf_id = request.form['verfahrens-id']
    tag = request.form['tag']
    vewendungszweck = request.form['verwendungszweck']
    laufzeitverfahren = request.form['laufzeit']
    auftraggeber = request.form['auftraggeber']
    verf_betreuung = request.form['verf_bet']
    kundenmanagement = request.form['kundenmanagement']
    fachadministration = request.form['fachadministration']

    try:
        cursor = get_cursor()
        query = """UPDATE fachverfahren SET name=%s, verf_id=%s, tag=%s, vewendungszweck=%s, laufzeitverfahren=%s, auftraggeber=%s, 
                verf_betreuung=%s, kundenmanagement=%s, fachadministration=%s WHERE tag=%s"""
        cursor.execute(query, (name, verf_id, tag, vewendungszweck, laufzeitverfahren,
                               auftraggeber, verf_betreuung, kundenmanagement, fachadministration, tag))
        get_db().commit()
        return redirect(url_for('fachverfahrenAnsehen', tag=tag))
    except Exception as e:
        return 'Fehler: ' + str(e)


@statzy.route('/fachverfahrenErstellen', methods=['POST'])
def fachverfahrenErstellen():
    tag = request.form['tag']
    edit = request.form['edit']
    if edit == '1':
        name = request.form['name']
        verf_id = request.form['verf_id']
        vewendungszweck = request.form['vewendungszweck']
        laufzeitverfahren = request.form['laufzeitverfahren']
        auftraggeber = request.form['auftraggeber']
        verf_betreuung = request.form['verf_betreuung']
        kundenmanagement = request.form['kundenmanagement']
        fachadministration = request.form['fachadministration']
        # ? wenn auftraggeber, verf_betreuung, kundenmanagement, fachadministration in der person Datenbank vorhanden sind, dann wird das form in die Datenbank fachverfahren geschrieben

        if personValidate(auftraggeber) and personValidate(verf_betreuung) and personValidate(kundenmanagement) and personValidate(fachadministration):
            try:
                cursor = get_cursor()
                print('test 1')
                query = "INSERT INTO fachverfahren (name, verf_id, tag, vewendungszweck, laufzeitverfahren, auftraggeber, verf_betreuung, kundenmanagement, fachadministration) VALUES ('" + name + "', '" + \
                    verf_id + "', '" + tag + "', '" + vewendungszweck + "', '" + laufzeitverfahren + "', '" + \
                        auftraggeber + "', '" + verf_betreuung + "', '" + \
                    kundenmanagement + "', '" + fachadministration + "')"
                print("test 2")
                cursor.execute(query)
                print("test 3")
                cursor.connection.commit()
                print("test 4")
                cursor.close()
                # debug print(query rückgabe)
                print('Fachverfahren wurde erstellt')
                return render_template('fachverfahrenAnsehen.html', tag=tag, name=name, verf_id=verf_id, vewendungszweck=vewendungszweck, laufzeitverfahren=laufzeitverfahren, auftraggeber=auftraggeber, verf_betreuung=verf_betreuung, kundenmanagement=kundenmanagement, fachadministration=fachadministration)
            except Exception as e:
                return 'Fehler: ' + str(e)
        else:
            return 'Diese Personen gibt es nicht '

    else:
        name = ''
        verf_id = ''
        vewendungszweck = ''
        laufzeitverfahren = ''
        auftraggeber = ''
        verf_betreuung = ''
        kundenmanagement = ''
        fachadministration = ''
    try:
        # ? wenn ein fehler bei der validierung auftritt werden die bereits eingetragen daten wieder angezeigt
        return render_template('fachverfahrenErstellen.html', tag=tag, name=name, verf_id=verf_id, vewendungszweck=vewendungszweck, laufzeitverfahren=laufzeitverfahren, auftraggeber=auftraggeber, verf_betreuung=verf_betreuung, kundenmanagement=kundenmanagement, fachadministration=fachadministration)
    except:
        return 'Fehler'


@statzy.route('/serverSuche')
def serverSuche():
    return render_template('serverSuche.html', warning=0)

@statzy.route('/serverAnsehen', methods=['GET', 'POST'])
def serverAnsehen():
    # ? Wenn die Methode POST ist, wird der Tag aus dem Formular genommen
    if request.method == 'POST':
        tag = request.form['tag']
        try:
            query = "SELECT name, verf_id, tag, vewendungszweck, laufzeitverfahren, auftraggeber, verf_betreuung, kundenmanagement, fachadministration FROM fachverfahren WHERE tag ~* '" + tag + "' ORDER BY name "
            results = db_execute(query)

            if not results:
                return render_template('ServerSuche.html', warning=1, tag=tag)

            name, verf_id, tag, vewendungszweck, laufzeitverfahren, auftraggeber, verf_betreuung, kundenmanagement, fachadministration = results[
                0]

            auftraggeber = personIdToName(auftraggeber)
            verf_betreuung = personIdToName(verf_betreuung)
            kundenmanagement = personIdToName(kundenmanagement)
            fachadministration = personIdToName(fachadministration)

            return render_template('serverAnsehen.html', name=name, verf_id=verf_id, tag=tag, vewendungszweck=vewendungszweck, laufzeitverfahren=laufzeitverfahren, auftraggeber=auftraggeber, verf_betreuung=verf_betreuung, kundenmanagement=kundenmanagement, fachadministration=fachadministration)
        except Exception as e:
            return 'Fehler' + str(e)
    # ? Wenn die Methode GET ist, wird der Tag aus der URL genommen
    else:
        tag = request.args.get('tag')
        try:
            query = "SELECT name, verf_id, tag, vewendungszweck, laufzeitverfahren, auftraggeber, verf_betreuung, kundenmanagement, fachadministration FROM fachverfahren WHERE tag ~* %s ORDER BY name"
            results = db_execute(query, (tag,))

            if not results:
                return render_template('ServerSuche.html', warning=1, tag=tag)

            name, verf_id, tag, vewendungszweck, laufzeitverfahren, auftraggeber, verf_betreuung, kundenmanagement, fachadministration = results[
                0]

            auftraggeber = personIdToName(auftraggeber)
            verf_betreuung = personIdToName(verf_betreuung)
            kundenmanagement = personIdToName(kundenmanagement)
            fachadministration = personIdToName(fachadministration)

            return render_template('serverAnsehen.html', name=name, verf_id=verf_id, tag=tag, vewendungszweck=vewendungszweck, laufzeitverfahren=laufzeitverfahren, auftraggeber=auftraggeber, verf_betreuung=verf_betreuung, kundenmanagement=kundenmanagement, fachadministration=fachadministration)
        except:
            return 'Fehler'

@statzy.route('/komponenteServer')
def komponenteServer():
    return render_template('komponenteServer.html')


@statzy.route('/login', methods=['POST'])
def login():
    session['username'] = request.form['username']
    session['password'] = request.form['password']
    try:
        get_db()
        return redirect(url_for('start'))
    except Exception as e:
        return 'Database connection failed! Login'


@statzy.route('/query', methods=['POST'])
def query():
    table_name = request.form['table']
    try:
        cursor = get_cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        results = cursor.fetchall()
        return render_template('query.html', table_name=table_name, data=results, cursor=cursor)
    except Exception as e:
        results = []
        return f"Database query failed! {e}"


@statzy.route('/datenbanken')
def datenbanken():
    try:
        cursor = get_cursor()
        cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
        tables = [table[0] for table in cursor.fetchall()]
        return render_template('datenbanken.html', tables=tables)
    except Exception as e:
        return 'Database connection failed! Datenbanken' + str(e)


if __name__ == '__main__':
    statzy.run(debug=True, host="0.0.0.0", port=5000)
