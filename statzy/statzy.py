from flask import Flask, render_template


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

@statzy.route('/komponenteServer')
def komponenteServer():
    return render_template('komponenteServer.html')





if __name__ == '__main__':
    statzy.run()
