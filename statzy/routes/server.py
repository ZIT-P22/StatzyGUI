from flask import Blueprint, render_template, request, session, redirect, url_for, json
from helper import get_cursor, db_execute, connection_pool, personValidate, get_db

bp_server = Blueprint('server', __name__)


@bp_server.route('/serverSuche')
def serverSuche():
    return render_template('serverSuche.html', warning=0)

@bp_server.route('/serverAnsehen', methods=['GET', 'POST'])
def serverAnsehen():
    if request.method == 'POST':
        name = request.form['name']
        try:
            query = "SELECT server_id, fachverfahren, name, umgebung, laufzeit_server, bereitstellungszeitpunkt, verwendungszweck, typ, netzwerk, ram, cpu, os, speichertyp, ""kapazität"", erreichbarkeit, ""hochverfügbarkeit"", vertraulichkeit, ""verfügbarkeit"", ""integrität"", anmerkungen, zeitpunkt_ins, user_ins, zeitpunkt_upd, user_upd  FROM server WHERE name ~* '" + name + "' ORDER BY name "
            results = db_execute(query)

            if not results:
                return render_template('serverSuche.html', warning=1, name=name)

            server_id, fachverfahren, name, umgebung, laufzeit_server, bereitstellungszeitpunkt, verwendungszweck, typ, netzwerk, ram, cpu, os, speichertyp, kapazität, erreichbarkeit, hochverfügbarkeit, vertraulichkeit, verfügbarkeit, integrität, anmerkungen, zeitpunkt_ins, user_ins, zeitpunkt_upd, user_upd = results[0]

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

            server_id, fachverfahren, name, umgebung, laufzeit_server, bereitstellungszeitpunkt, verwendungszweck, typ, netzwerk, ram, cpu, os, speichertyp, kapazität, erreichbarkeit, hochverfügbarkeit, vertraulichkeit, verfügbarkeit, integrität, anmerkungen, zeitpunkt_ins, user_ins, zeitpunkt_upd, user_upd = results[0]

            return render_template('serverAnsehen.html', name=name, server_id=server_id, fachverfahren=fachverfahren, umgebung=umgebung, laufzeit_server=laufzeit_server, bereitstellungszeitpunkt=bereitstellungszeitpunkt, verwendungszweck=verwendungszweck, typ=typ, netzwerk=netzwerk, ram=ram, cpu=cpu, os=os, speichertyp=speichertyp, kapazität=kapazität, erreichbarkeit=erreichbarkeit, hochverfügbarkeit=hochverfügbarkeit, vertraulichkeit=vertraulichkeit, verfügbarkeit=verfügbarkeit, integrität=integrität, anmerkungen=anmerkungen, zeitpunkt_ins=zeitpunkt_ins, user_ins=user_ins, zeitpunkt_upd=zeitpunkt_upd, user_upd=user_upd)
        except Exception as e:
            return 'Fehler: ' + str(e)
   
   
        
@bp_server.route('/serverErstellen', methods=['POST'])
def serverErstellen():
    name = request.form['name']
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
                query = "INSERT INTO fachverfahren (name, verf_id, vewendungszweck, laufzeitverfahren, auftraggeber, verf_betreuung, kundenmanagement, fachadministration) VALUES ('" + name + "', '" + \
                    verf_id + "', '" + name + "', '" + vewendungszweck + "', '" + laufzeitverfahren + "', '" + \
                        auftraggeber + "', '" + verf_betreuung + "', '" + \
                    kundenmanagement + "', '" + fachadministration + "')"
                print("test 2")
                cursor.execute(query)
                print("test 3")
                cursor.connection.commit()
                print("test 4")
                cursor.close()
                # debug print(query rückgabe)
                print('Server wurde erstellt')
                return render_template('serverAnsehen.html', name=name, verf_id=verf_id, vewendungszweck=vewendungszweck, laufzeitverfahren=laufzeitverfahren, auftraggeber=auftraggeber, verf_betreuung=verf_betreuung, kundenmanagement=kundenmanagement, fachadministration=fachadministration)
            except Exception as e:
                return 'Fehler: ' + str(e)
        else:
            return 'Diesen Server gibt es nicht '


@bp_server.route('/serverEditieren', methods=['POST'])
def serverEditieren():
    name = request.form['name']
    try:
        query = "SELECT name, verf_id, vewendungszweck, laufzeitverfahren, auftraggeber, verf_betreuung, kundenmanagement, fachadministration FROM fachverfahren WHERE tag ~* '" + name + "' ORDER BY name "
        results = db_execute(query)

        name, verf_id, vewendungszweck, laufzeitverfahren, auftraggeber, verf_betreuung, kundenmanagement, fachadministration = results[
            0]
        return render_template('serverEditieren.html', name=name, verf_id=verf_id, vewendungszweck=vewendungszweck, laufzeitverfahren=laufzeitverfahren, auftraggeber=auftraggeber, verf_betreuung=verf_betreuung, kundenmanagement=kundenmanagement, fachadministration=fachadministration)
    except:
        return 'Fehler'

    
@bp_server.route('/serverUpdate', methods=['POST'])
def serverUpdate():
    name = request.form['it-verfahren-namen']
    verf_id = request.form['verfahrens-id']
    vewendungszweck = request.form['verwendungszweck']
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
        return redirect(url_for('fachverfahren.fachverfahrenAnsehen', name=name))
    except Exception as e:
        return 'Fehler: ' + str(e)
    
    
@bp_server.route('/komponenteServer')
def komponenteServer():
    return render_template('komponenteServer.html')