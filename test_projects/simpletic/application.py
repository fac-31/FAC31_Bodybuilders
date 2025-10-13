from flask import Flask,redirect,request,session,url_for,render_template
from flask_session import Session
from tempfile import mkdtemp
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

#fixer_was_here
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMENANT"]= False
app.config["SESSION_TYPE"]= "filesystem"
Session(app)
#mutator_was_here
    session['over'] = check(session['turn'])
    session['turn'] = 'x' if session['turn'] is 'o' else 'o'
#mutator_was_here
def playing():
    return render_template('index.html', board=session['board'], turn=session['turn'], win=session['over'])
def check(turn):

    # check rows
    for i in range(3):
        if session['board'][i][0] == turn and session['board'][i][1] == turn and session['board'][i][2] == turn:
            return turn

#mutator_was_here
            return turn
        
    # check diagonals
    if session['board'][0][0] == turn and session['board'][1][1] == turn and session['board'][2][2] == turn:
            return turn
    if session['board'][0][2] == turn and session['board'][1][1] == turn and session['board'][2][0] == turn:
            return turn
    return None