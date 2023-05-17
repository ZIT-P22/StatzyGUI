from flask import Flask, render_template, request, redirect, url_for, session, g, jsonify
import psycopg2
from psycopg2 import pool
import secrets
import json

statzy = Flask(__name__)
statzy.secret_key = secrets.token_hex(16)


#! def zone start

# Create a connection pool
connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=40,
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
        \
        str(person_id) + "'"
    results = db_execute(query)
    return results[0][0] if results else None


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


@statzy.route('/getnames', methods=['GET'])
def getnames():
    input = request.args.get('input')
    cursor = get_cursor()
    cursor.execute("SELECT person_id, vornam, name, dez FROM person WHERE name ILIKE %s OR vornam ILIKE %s OR dez ILIKE %s",

                   (f"%{input}%", f"%{input}%", f"%{input}%",))
    results = cursor.fetchall()
    names = [{"person_id": result[0], "vornam": result[1],

              "name": result[2], "dez": result[3]} for result in results]
    return json.dumps(names)


@statzy.route('/person')
def person():
    return render_template('person.html') 


@statzy.route('/personSuche')
def personSuche():
    return render_template('personSuche.html', warning=0)


@statzy.route('/personAnsehen', methods=['GET', 'POST'])
def personAnsehen():
    if request.method == 'POST':
        # print("Post")
        name = request.form['name']
        try:
            cursor = get_cursor()
            query = "SELECT name, telefonnummer, dez, vornam, person_id, zeitpunkt_ins, user_ins, zeitpunkt_upd, user_upd FROM person WHERE name ~* '" + name + "' ORDER BY name "
            cursor.execute(query)
            results = cursor.fetchall()
            # print(results)

            if not results:
                # print("No results")
                return render_template('person.html', warning=1, name=name)

            name, telefonnummer, dez, vornam, person_id, zeitpunkt_ins, user_ins, zeitpunkt_upd, user_upd = results[
                0]

            return render_template('personAnsehen.html', name=name, telefonnummer=telefonnummer, dez=dez, vornam=vornam, person_id=person_id, zeitpunkt_ins=zeitpunkt_ins, user_ins=user_ins, zeitpunkt_upd=zeitpunkt_upd, user_upd=user_upd)
        except Exception as e:
            return 'Fehler', e
    else:
        # print("Get")
        name = request.args.get('name')
        # print(name)
        try:
            cursor = get_cursor()
            # print("test1")
            query = "SELECT name, telefonnummer, dez, vornam, person_id, zeitpunkt_ins, user_ins, zeitpunkt_upd, user_upd FROM person WHERE name ~* '" + name + "' ORDER BY name"
            # print("test2")
            cursor.execute(query, (name,))
            # print("test3")
            results = cursor.fetchall()
            # print(results)
            if not results:
                # print("test5")
                return render_template('person.html', warning=1, name=name)
            name, telefonnummer, dez, vornam, person_id, zeitpunkt_ins, user_ins, zeitpunkt_upd, user_upd = results[
                0]
            # print("test6")
            return render_template('personAnsehen.html', name=name, telefonnummer=telefonnummer, dez=dez, vornam=vornam, person_id=person_id, zeitpunkt_ins=zeitpunkt_ins, user_ins=user_ins, zeitpunkt_upd=zeitpunkt_upd, user_upd=user_upd)
        except Exception as e:
            return 'Fehler', e


@statzy.route('/personEditieren', methods=['POST'])
def personEditieren():
    print("Test 1")
    # nameOld = request.form['name']
    # print(nameOld)
    name = request.form['name']
    print(name)
    try:
        cursor = get_cursor()
        query = "SELECT name, telefonnummer, dez, vornam, person_id, zeitpunkt_ins, user_ins, zeitpunkt_upd, user_upd FROM person WHERE name ~* '" + name + "' ORDER BY name"
        cursor.execute(query)
        results = cursor.fetchall()
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
    person_id = request.form['person_id']
    # zeitpunkt_ins = request.form['zeitpunkt_ins']
    # user_ins = request.form['user_ins']
    # zeitpunkt_upd = request.form['zeitpunkt_upd']
    # user_upd = request.form['user_upd']
    # zeitpunkt_ins=NULL, user_ins=NULL, zeitpunkt_upd=NULL, user_upd=NULL
    try:
        cursor = get_cursor()
        query = "UPDATE person SET name=%s, telefonnummer=%s, dez=%s, vornam=%s WHERE person_id=%s"
        # print(query, (name, telefonnummer, dez, vornam, name))
        cursor.execute(query, (name, telefonnummer, dez, vornam, person_id))
        get_db().commit()
        return redirect(url_for('personAnsehen', name=name))
    except Exception as e:
        return 'Fehler: ' + str(e)


@statzy.route('/personValidate', methods=['POST'])
def personValidate():
    return render_template('personErstellen.html')


@statzy.route('/personErstellen', methods=['POST'])
def personErstellen():
    name = request.form['name']
    telefonnummer = request.form['telefonnummer']
    dez = request.form['dez']
    vornam = request.form['vornam']
    print("test 0")
    try:
        cursor = get_cursor()
        print('test 1')
        query = "INSERT INTO person (name, telefonnummer, dez, vornam) VALUES ('" + name + "', '" + \
            telefonnummer + "', '" + dez + "', '" + vornam + "')"
        print("test 2")
        cursor.execute(query)
        print("test 3")
        cursor.connection.commit()
        print("test 4")
        cursor.close()
        # debug print(query rückgabe)
        print('Person wurde erstellt')
        return render_template('personAnsehen.html', name=name, telefonnummer=telefonnummer, dez=dez, vornam=vornam)
    except Exception as e:
        return 'Fehler: ' + str(e)


@statzy.route('/fachverfahrenSuche')
def fachverfahrenSuche():
    return render_template('fachverfahrenSuche.html', warning=0)


@statzy.route('/persServRelAnsehen')
def persServRelAnsehen():
    try:
        results = db_execute("SELECT * FROM person")
        return render_template('persServRelAnsehen.html', data=results)
    except Exception as e:
        results = []
        return f"Database query failed! {e}"


@statzy.route('/fachverfahrenAnsehen', methods=['GET', 'POST'])
def fachverfahrenAnsehen():
    if request.method == 'POST':
        # get tag from form
        tag = request.form['tag']
    else:
        # get tag from url param
        tag = request.args.get('tag')

    try:
        # execute query with parameterized query
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
    except Exception as e:
        return 'Fehler' + str(e)


@statzy.route('/fachverfahrenEditieren', methods=['POST'])
def fachverfahrenEditieren():
    tag = request.form['tag']
    try:
        query = "SELECT name, verf_id, tag, vewendungszweck, laufzeitverfahren, auftraggeber, verf_betreuung, kundenmanagement, fachadministration FROM fachverfahren WHERE tag ~* '" + tag + "' ORDER BY name "
        results = db_execute(query)

        name, verf_id, tag, vewendungszweck, laufzeitverfahren, auftraggeber_id, verf_betreuung_id, kundenmanagement_id, fachadministration_id = results[
            0]
        auftraggeber = personIdToName(auftraggeber_id)
        verf_betreuung = personIdToName(verf_betreuung_id)
        kundenmanagement = personIdToName(kundenmanagement_id)
        fachadministration = personIdToName(fachadministration_id)

        print("name:", name)
        print("verf_id:", verf_id)
        print("tag:", tag)
        print("vewendungszweck:", vewendungszweck)
        print("laufzeitverfahren:", laufzeitverfahren)
        print("auftraggeber:", auftraggeber)
        print("verf_betreuung:", verf_betreuung)
        print("kundenmanagement:", kundenmanagement)
        print("fachadministration:", fachadministration)

        return render_template('fachverfahrenEditieren.html', name=name, verf_id=verf_id, tag=tag, vewendungszweck=vewendungszweck, laufzeitverfahren=laufzeitverfahren, auftraggeber=auftraggeber, verf_betreuung=verf_betreuung, kundenmanagement=kundenmanagement, fachadministration=fachadministration)
    except:
        return 'Fehler'


@statzy.route('/fachverfahrenUpdate', methods=['POST'])
def fachverfahrenUpdate():
    tag = request.form['tag'] if request.form['tag'] else None
    if not tag:
        return 'Fehler: Kein Tag bereitgestellt.'

    # Fetch current data for this row.
    cursor = get_cursor()
    query = """SELECT * FROM fachverfahren WHERE tag=%s"""
    cursor.execute(query, (tag,))
    current_data = cursor.fetchone()

    # Convert the result tuple to a dictionary.
    current_data_dict = {desc[0]: value for desc,
                         value in zip(cursor.description, current_data)}

    # Replace any None values with current data.
    name = request.form['it-verfahren-namen'] if request.form['it-verfahren-namen'] else current_data_dict['name']
    verf_id = request.form['verfahrens-id'] if request.form['verfahrens-id'] else current_data_dict['verf_id']
    vewendungszweck = request.form['verwendungszweck'] if request.form[
        'verwendungszweck'] else current_data_dict['vewendungszweck']
    laufzeitverfahren = request.form['laufzeit'] if request.form['laufzeit'] else current_data_dict['laufzeitverfahren']
    auftraggeber_id = request.form['auftraggeber-id'] if request.form['auftraggeber-id'] else current_data_dict['auftraggeber']
    verf_betreuung_id = request.form['verf_bet-id'] if request.form['verf_bet-id'] else current_data_dict['verf_betreuung']
    kundenmanagement_id = request.form['kundenmanagement-id'] if request.form['kundenmanagement-id'] else current_data_dict['kundenmanagement']
    fachadministration_id = request.form['fachadmin-id'] if request.form['fachadmin-id'] else current_data_dict['fachadministration']

    print("auftraggeber_id:", auftraggeber_id)
    print("verf_betreuung_id:", verf_betreuung_id)
    print("kundenmanagement_id:", kundenmanagement_id)
    print("fachadministration_id:", fachadministration_id)

    try:
        query = """UPDATE fachverfahren SET name=%s, verf_id=%s, tag=%s, vewendungszweck=%s, laufzeitverfahren=%s, auftraggeber=%s, 
                verf_betreuung=%s, kundenmanagement=%s, fachadministration=%s WHERE tag=%s"""
        cursor.execute(query, (name, verf_id, tag, vewendungszweck, laufzeitverfahren,
                       auftraggeber_id, verf_betreuung_id, kundenmanagement_id, fachadministration_id, tag))
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
    if request.method == 'POST':
        name = request.form['name']
        try:
            query = "SELECT server_id, fachverfahren, name, umgebung, laufzeit_server, bereitstellungszeitpunkt, verwendungszweck, typ, netzwerk, ram, cpu, os, speichertyp, ""kapazität"", erreichbarkeit, ""hochverfügbarkeit"", vertraulichkeit, ""verfügbarkeit"", ""integrität"", anmerkungen, zeitpunkt_ins, user_ins, zeitpunkt_upd, user_upd  FROM server WHERE name ~* '" + name + "' ORDER BY name "
            results = db_execute(query)

            if not results:
                return render_template('serverSuche.html', warning=1, name=name)

            server_id, fachverfahren, name, umgebung, laufzeit_server, bereitstellungszeitpunkt, verwendungszweck, typ, netzwerk, ram, cpu, os, speichertyp, kapazität, erreichbarkeit, hochverfügbarkeit, vertraulichkeit, verfügbarkeit, integrität, anmerkungen, zeitpunkt_ins, user_ins, zeitpunkt_upd, user_upd = results[
                0]

            return render_template('serverAnsehen.html', name=name, server_id=server_id, fachverfahren=fachverfahren, umgebung=umgebung, laufzeit_server=laufzeit_server, bereitstellungszeitpunkt=bereitstellungszeitpunkt, verwendungszweck=verwendungszweck, typ=typ, netzwerk=netzwerk, ram=ram, cpu=cpu, os=os, speichertyp=speichertyp, kapazität=kapazität, erreichbarkeit=erreichbarkeit, hochverfügbarkeit=hochverfügbarkeit, vertraulichkeit=vertraulichkeit, verfügbarkeit=verfügbarkeit, integrität=integrität, anmerkungen=anmerkungen, zeitpunkt_ins=zeitpunkt_ins, user_ins=user_ins, zeitpunkt_upd=zeitpunkt_upd, user_upd=user_upd)
        except Exception as e:
            return 'Fehler: ' + str(e)
    else:
        name = request.args.get('name')
        try:
            query = "SELECT server_id, fachverfahren, name, umgebung, laufzeit_server, bereitstellungszeitpunkt, verwendungszweck, typ, netzwerk, ram, cpu, os, speichertyp, ""kapazität"", erreichbarkeit, ""hochverfügbarkeit"", vertraulichkeit, ""verfügbarkeit"", ""integrität"", anmerkungen, zeitpunkt_ins, user_ins, zeitpunkt_upd, user_upd  FROM server WHERE name ~* '" + name + "' ORDER BY name "
            results = db_execute(query)

            if not results:
                return render_template('serverSuche.html', warning=1, name=name)

            server_id, fachverfahren, name, umgebung, laufzeit_server, bereitstellungszeitpunkt, verwendungszweck, typ, netzwerk, ram, cpu, os, speichertyp, kapazität, erreichbarkeit, hochverfügbarkeit, vertraulichkeit, verfügbarkeit, integrität, anmerkungen, zeitpunkt_ins, user_ins, zeitpunkt_upd, user_upd = results[
                0]

            return render_template('serverAnsehen.html', name=name, server_id=server_id, fachverfahren=fachverfahren, umgebung=umgebung, laufzeit_server=laufzeit_server, bereitstellungszeitpunkt=bereitstellungszeitpunkt, verwendungszweck=verwendungszweck, typ=typ, netzwerk=netzwerk, ram=ram, cpu=cpu, os=os, speichertyp=speichertyp, kapazität=kapazität, erreichbarkeit=erreichbarkeit, hochverfügbarkeit=hochverfügbarkeit, vertraulichkeit=vertraulichkeit, verfügbarkeit=verfügbarkeit, integrität=integrität, anmerkungen=anmerkungen, zeitpunkt_ins=zeitpunkt_ins, user_ins=user_ins, zeitpunkt_upd=zeitpunkt_upd, user_upd=user_upd)
        except Exception as e:
            return 'Fehler: ' + str(e)


@statzy.route('/serverErstellen', methods=['POST'])
def serverErstellen():
    name = request.form.get('name', '')
    edit = request.form.get('edit', '')
    if edit == '1':
        server_id = request.form['server_id']
        fachverfahren = request.form['fachverfahren']
        umgebung = request.form['umgebung']
        laufzeit_server = request.form['laufzeit_server']
        bereitstellungszeitpunkt = request.form['bereitstellungszeitpunkt']
        verwendungszweck = request.form['vewendungszweck']
        typ = request.form['typ']
        netzwerk = request.form['netzwerk']
        ram = request.form['ram']
        cpu = request.form['cpu']
        os = request.form['os']
        speichertyp = request.form['speichertyp']
        kapazität = request.form['kapazität']
        erreichbarkeit = request.form['erreichbarkeit']
        hochverfügbarkeit = request.form['hochverfügbarkeit']
        vertraulichkeit = request.form['vertraulichkeit']
        verfügbarkeit = request.form['verfügbarkeit']
        integrität = request.form['integrität']
        anmerkungen = request.form['anmerkungen']
        zeitpunkt_ins = request.form['zeitpunkt_ins']
        user_ins = request.form['user_ins']
        zeitpunkt_upd = request.form['zeitpunkt_upd']
        user_upd = request.form['user_upd']
        # ? wenn auftraggeber, verf_betreuung, kundenmanagement, fachadministration in der person Datenbank vorhanden sind, dann wird das form in die Datenbank fachverfahren geschrieben

        if personValidate(user_ins) and personValidate(user_upd):
            try:
                cursor = get_cursor()
                print('test 1')
                query = "INSERT INTO server (server_id, fachverfahren, name, umgebung, laufzeit_server, bereitstellungszeitpunkt, verwendungszweck, typ, netzwerk, ram, cpu, os, speichertyp, ""kapazität"", erreichbarkeit, ""hochverfügbarkeit"", vertraulichkeit, ""verfügbarkeit"", ""integrität"", anmerkungen, zeitpunkt_ins, user_ins, zeitpunkt_upd, user_upd) VALUES ('" + server_id + "', '" + \
                    fachverfahren + "', '" + name + "', '" + umgebung + "', '" + laufzeit_server + "', '" + bereitstellungszeitpunkt + "', '" + verwendungszweck + "', '" + \
                        typ + "', '" + netzwerk + "', '" + ram + "', '" + cpu + "', '" + os + "', '" + speichertyp + "', '" + \
                        kapazität + "', '" + erreichbarkeit + "', '" + hochverfügbarkeit + "', '" + hochverfügbarkeit + "', '" + vertraulichkeit + "', '" + \
                        verfügbarkeit + "', '" + integrität + "', '" + anmerkungen + "', '" + zeitpunkt_ins + "', '" + \
                        user_ins + "', '" + zeitpunkt_upd + "', '" + user_upd + "')"
                print("test 2")
                cursor.execute(query)
                print("test 3")
                cursor.connection.commit()
                print("test 4")
                cursor.close()
                # debug print(query rückgabe)
                print('Server wurde erstellt')
                return render_template('serverAnsehen.html', name=name, server_id=server_id, fachverfahren=fachverfahren, umgebung=umgebung, laufzeit_server=laufzeit_server, bereitstellungszeitpunkt=bereitstellungszeitpunkt, verwendungszweck=verwendungszweck, typ=typ, netzwerk=netzwerk, ram=ram, cpu=cpu, os=os, speichertyp=speichertyp, kapazität=kapazität, erreichbarkeit=erreichbarkeit, hochverfügbarkeit=hochverfügbarkeit, vertraulichkeit=vertraulichkeit, verfügbarkeit=verfügbarkeit, integrität=integrität, anmerkungen=anmerkungen, zeitpunkt_ins=zeitpunkt_ins, user_ins=user_ins, zeitpunkt_upd=zeitpunkt_upd, user_upd=user_upd)
            except Exception as e:
                return 'Fehler: ' + str(e)
        else:
            return 'Diese Person gibt es nicht '
    else:
        server_id = ''
        fachverfahren = ''
        name = ''
        umgebung = ''
        laufzeit_server = ''
        bereitstellungszeitpunkt = ''
        verwendungszweck = ''
        typ = ''
        netzwerk = ''
        ram = ''
        cpu = ''
        os = ''
        speichertyp = ''
        kapazität = ''
        erreichbarkeit = ''
        hochverfügbarkeit = ''
        vertraulichkeit = ''
        verfügbarkeit = ''
        integrität = ''
        anmerkungen = ''
        zeitpunkt_ins = ''
        user_ins = ''
        zeitpunkt_upd = ''
        user_upd = ''
    try:
        # ? wenn ein fehler bei der validierung auftritt werden die bereits eingetragen daten wieder angezeigt
        return render_template('serverErstellen.html', name=name, server_id=server_id, fachverfahren=fachverfahren, umgebung=umgebung, laufzeit_server=laufzeit_server, bereitstellungszeitpunkt=bereitstellungszeitpunkt, verwendungszweck=verwendungszweck, typ=typ, netzwerk=netzwerk, ram=ram, cpu=cpu, os=os, speichertyp=speichertyp, kapazität=kapazität, erreichbarkeit=erreichbarkeit, hochverfügbarkeit=hochverfügbarkeit, vertraulichkeit=vertraulichkeit, verfügbarkeit=verfügbarkeit, integrität=integrität, anmerkungen=anmerkungen, zeitpunkt_ins=zeitpunkt_ins, user_ins=user_ins, zeitpunkt_upd=zeitpunkt_upd, user_upd=user_upd)
    except:
        return 'Fehler'


@statzy.route('/serverEditieren', methods=['POST'])
def serverEditieren():
    name = request.form['name']
    try:
        query = "SELECT server_id, fachverfahren, name, umgebung, laufzeit_server, bereitstellungszeitpunkt, verwendungszweck, typ, netzwerk, ram, cpu, os, speichertyp, kapazität, erreichbarkeit, hochverfügbarkeit, vertraulichkeit, verfügbarkeit, integrität, anmerkungen, zeitpunkt_ins, user_ins, zeitpunkt_upd, user_upd FROM server WHERE name ILIKE %s ORDER BY name"
        results = db_execute(query, (name,))  # Pass the parameter as a tuple

        if results:
            server_id, fachverfahren, name, umgebung, laufzeit_server, bereitstellungszeitpunkt, verwendungszweck, typ, netzwerk, ram, cpu, os, speichertyp, kapazität, erreichbarkeit, hochverfügbarkeit, vertraulichkeit, verfügbarkeit, integrität, anmerkungen, zeitpunkt_ins, user_ins, zeitpunkt_upd, user_upd = results[0]

            return render_template('serverEditieren.html', name=name, server_id=server_id, fachverfahren=fachverfahren, umgebung=umgebung, laufzeit_server=laufzeit_server, bereitstellungszeitpunkt=bereitstellungszeitpunkt, verwendungszweck=verwendungszweck, typ=typ, netzwerk=netzwerk, ram=ram, cpu=cpu, os=os, speichertyp=speichertyp, kapazität=kapazität, erreichbarkeit=erreichbarkeit, hochverfügbarkeit=hochverfügbarkeit, vertraulichkeit=vertraulichkeit, verfügbarkeit=verfügbarkeit, integrität=integrität, anmerkungen=anmerkungen, zeitpunkt_ins=zeitpunkt_ins, user_ins=user_ins, zeitpunkt_upd=zeitpunkt_upd, user_upd=user_upd)

        return 'No results found.'
    except KeyError:
        return 'Bad Request: Missing "name" parameter.'
    except Exception as e:
        return f'Error: {str(e)}'


@statzy.route('/serverUpdate', methods=['POST'])
def serverUpdate():
    name = request.form['it-verfahren-namen']
    verf_id = request.form['verfahrens-id']
    verwendungszweck = request.form['verwendungszweck']
    laufzeitverfahren = request.form['laufzeit']
    auftraggeber = request.form['auftraggeber']
    verf_betreuung = request.form['verf_bet']
    kundenmanagement = request.form['kundenmanagement']
    fachadministration = request.form['fachadministration']

    try:
        cursor = get_cursor()
        query = """UPDATE server SET name=%s, verf_id=%s, vewendungszweck=%s, laufzeitverfahren=%s, auftraggeber=%s, 
                verf_betreuung=%s, kundenmanagement=%s, fachadministration=%s WHERE name=%s"""
        cursor.execute(query, (name, verf_id, vewendungszweck, laufzeitverfahren,
                               auftraggeber, verf_betreuung, kundenmanagement, fachadministration, name))
        get_db().commit()
        return redirect(url_for('serverAnsehen', name=name))
    except Exception as e:
        return 'Fehler: ' + str(e)


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
