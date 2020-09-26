from flask import Flask, render_template, request
#from flaskwebgui import FlaskUI   # get the FlaskUI class

from trasker import Trask, Analyzer
import subprocess

# global
app = Flask(__name__)
python_analyzer = Analyzer(language='python')
#ui = FlaskUI(app)                 # feed the parameters

# functions
def on_refresh_btn():
    print("refresh btn pressed !")

def open_file_at_line(filename, line_nb):
    arg = filename+':'+str(line_nb)
    subprocess.Popen(["code.cmd", "--goto", arg]) # open file with vscode

def on_test_btn():
    pass

def on_locate_trask(filename, line_nb):
    open_file_at_line(filename, line_nb)



# flask routing
@app.route("/")
def index():
    trasks = python_analyzer.inspect_file('sample_test_file.py')

    todo_trasks = [t for t in trasks if t.trask_type=='todo']
    doing_trasks = [t for t in trasks if t.trask_type=='doing']
    done_trasks = [t for t in trasks if t.trask_type=='done']
    other_trasks = [t for t in trasks if (t.trask_type!='todo' and t.trask_type!='doing' and t.trask_type!='done')]

    return render_template('ui.html', todo_trasks=todo_trasks, doing_trasks=doing_trasks, done_trasks=done_trasks, other_trasks=other_trasks)

#background process happening without any refreshing
@app.route('/background_process_test')
def background_process_test():
    on_test_btn()
    return ("nothing")

@app.route('/background_locate')
def background_locate():
    filename = request.args.get('file', 0, type=str)
    line_nb = request.args.get('line', 0, type=int)
    print('locating {}:{}'.format(filename, line_nb))
    on_locate_trask(filename, line_nb)
    return ("nothing")

def main():
    #ui.run()                           # call the 'run' method
    app.run()

if __name__ == "__main__":
    main()


