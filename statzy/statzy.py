from flask import Flask, render_template, request, redirect, url_for, session, g
import psycopg2
import secrets

statzy = Flask(__name__)
statzy.secret_key = secrets.token_hex(16)



#! def zone start

def personValidate(person_id):
    cursor = conn.cursor()
    query = "SELECT count(*) FROM person WHERE person_id = '" + person_id + "'"
    cursor.execute(query)
    results = cursor.fetchall()
    
    if results[0][0] == 1:
        return True
    else:
        return False
    

#! def zone end




#! def zone start

def personValidate(person_id):
    cursor = conn.cursor()
    query = "SELECT count(*) FROM person WHERE person_id = '" + person_id + "'"
    cursor.execute(query)
    results = cursor.fetchall()
    
    if results[0][0] == 1:
        return True
    else:
        return False
    

#! def zone end



def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(
            dbname='statzy',
            # user=session.get('username'),
            # password=session.get('password'),
            password='postgres',
            user='postgres',
            host='10.128.201.123',
            port='5432'
        )
    return g.db


def get_cursor():
    if 'cursor' not in g:
        g.cursor = get_db().cursor()
    return g.cursor


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
    return render_template('index.html')


@statzy.route('/person')
def person():
    return render_template('person.html')


@statzy.route('/fachverfahrenSuche')
def fachverfahrenSuche():
    return render_template('fachverfahrenSuche.html', warning=0)


@statzy.route('/fachverfahrenAnsehen', methods=['GET', 'POST'])
def fachverfahrenAnsehen():
    if request.method == 'POST':
        tag = request.form['tag']
        try:
            cursor = get_cursor()
            query = "SELECT name, verf_id, tag, vewendungszweck, laufzeitverfahren, auftraggeber, verf_betreuung, kundenmanagement, fachadministration FROM fachverfahren WHERE tag ~* '" + tag + "' ORDER BY name "
            cursor.execute(query)
            results = cursor.fetchall()

            if not results:
                return render_template('fachverfahrenSuche.html', warning=1, tag=tag)

            name, verf_id, tag, vewendungszweck, laufzeitverfahren, auftraggeber, verf_betreuung, kundenmanagement, fachadministration = results[
                0]
            return render_template('fachverfahrenAnsehen.html', name=name, verf_id=verf_id, tag=tag, vewendungszweck=vewendungszweck, laufzeitverfahren=laufzeitverfahren, auftraggeber=auftraggeber, verf_betreuung=verf_betreuung, kundenmanagement=kundenmanagement, fachadministration=fachadministration)
        except:
            return 'Fehler'
    else:
        tag = request.args.get('tag')
        try:
            cursor = get_cursor()
            query = "SELECT name, verf_id, tag, vewendungszweck, laufzeitverfahren, auftraggeber, verf_betreuung, kundenmanagement, fachadministration FROM fachverfahren WHERE tag ~* %s ORDER BY name"
            cursor.execute(query, (tag,))
            results = cursor.fetchall()

            if not results:
                return render_template('fachverfahrenSuche.html', warning=1, tag=tag)

            name, verf_id, tag, vewendungszweck, laufzeitverfahren, auftraggeber, verf_betreuung, kundenmanagement, fachadministration = results[
                0]
            return render_template('fachverfahrenAnsehen.html', name=name, verf_id=verf_id, tag=tag, vewendungszweck=vewendungszweck, laufzeitverfahren=laufzeitverfahren, auftraggeber=auftraggeber, verf_betreuung=verf_betreuung, kundenmanagement=kundenmanagement, fachadministration=fachadministration)
        except:
            return 'Fehler'


@statzy.route('/fachverfahrenEditieren', methods=['POST'])
def fachverfahrenEditieren():
    tag = request.form['tag']
    try:
        cursor = get_cursor()
        query = "SELECT name, verf_id, tag, vewendungszweck, laufzeitverfahren, auftraggeber, verf_betreuung, kundenmanagement, fachadministration FROM fachverfahren WHERE tag ~* '" + tag + "' ORDER BY name "
        cursor.execute(query)
        results = cursor.fetchall()

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
        #? wenn auftraggeber, verf_betreuung, kundenmanagement, fachadministration in der person Datenbank vorhanden sind, dann wird das form in die Datenbank fachverfahren geschrieben
        
        
        if personValidate(auftraggeber) and personValidate(verf_betreuung) and personValidate(kundenmanagement) and personValidate(fachadministration):
            try:
                cursor = conn.cursor()
                query = "INSERT INTO fachverfahren (name, verf_id, tag, vewendungszweck, laufzeitverfahren, auftraggeber, verf_betreuung, kundenmanagement, fachadministation) VALUES ('" + name + "', '" + verf_id + "', '" + tag + "', '" + vewendungszweck + "', '" + laufzeitverfahren + "', '" + auftraggeber + "', '" + verf_betreuung + "', '" + kundenmanagement + "', '" + fachadministration + "')"
                cursor.execute(query)
                conn.commit()
                return render_template('fachverfahrenErstellen.html', tag=tag, name=name, verf_id=verf_id, vewendungszweck=vewendungszweck, laufzeitverfahren=laufzeitverfahren, auftraggeber=auftraggeber, verf_betreuung=verf_betreuung, kundenmanagement=kundenmanagement, fachadministration=fachadministration)
            except:
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
        return render_template('fachverfahrenErstellen.html', tag=tag, name=name, verf_id=verf_id, vewendungszweck=vewendungszweck, laufzeitverfahren=laufzeitverfahren, auftraggeber=auftraggeber, verf_betreuung=verf_betreuung, kundenmanagement=kundenmanagement, fachadministration=fachadministration)
    except:
        return 'Fehler'


@statzy.route('/server')
def server():
    return render_template('server.html')


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
