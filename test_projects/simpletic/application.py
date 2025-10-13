from flask import Flask,redirect,request,session,url_for,render_template
from flask_session import Session
from tempfile import mkdtemp
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# session config
app.config["SESSION_FILE_DIR"]= mkdtemp()
app.config["SESSION_PERMENANT"]= False
app.config["SESSION_TYPE"]= "filesystem"
Session(app)

@app.route("/")
def index():
    session['board'] = [[None,None,None],[None,None,None],[None,None,None]]
    session['turn'] = 'x'
    session['over'] = None
    return render_template('index.html', board=session['board'], turn=session['turn'])

@app.route('/play/<int:row>/<int:col>')
def play(row,col):
    i = row
    j = col
    session['board'][i][j] = session['turn']
    session['over'] = check(session['turn'])
    session['turn'] = 'x' if session['turn'] is 'o' else 'o'
    return redirect('/playing')

@app.route('/playing')
def playing():
    return render_template('index.html', board=session['board'], turn=session['turn'], win=session['over'])
def check(turn):

    # check rows
    for i in range(3):
        if session['board'][i][0] == turn and session['board'][i][1] == turn and session['board'][i][2] == turn:
            return turn

    # check cols
    for i in range(3):
        if session['board'][0][i] == turn and session['board'][1][i] == turn and session['board'][2][i] == turn:
            return turn
        
    # check diagonals
    if session['board'][0][0] == turn and session['board'][1][1] == turn and session['board'][2][2] == turn:
            return turn
    if session['board'][0][2] == turn and session['board'][1][1] == turn and session['board'][2][0] == turn:
            return turn
    return None
