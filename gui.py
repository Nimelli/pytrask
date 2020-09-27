from flask import Flask, render_template, request

from trasker import Trask, Analyzer
import subprocess
from flaskwebgui import FlaskUI

supported_editor = {
    'vscode':{
        'app': "code.cmd",
        'cmd': "--goto",
        'arg': "{filename}:{line_nb}"
    },
    'sublime':{
        'app': "subl",
        'cmd': "",
        'arg': "{filename}:{line_nb}"
    },
}

class AppUX():
    def __init__(self):
        self.python_analyzer = Analyzer(language='python')
        self.all_trasks = []
        self.text_editor = 'vscode' #by default

    def set_editor(self, editor):
        if editor in list(supported_editor.keys()):
            self.text_editor = editor

    def open_file_at_line(self, filename, line_nb):

        app = supported_editor[self.text_editor]['app']
        cmd = supported_editor[self.text_editor]['cmd']
        arg = supported_editor[self.text_editor]['arg']

        subprocess.Popen([app, cmd, arg.format(filename=filename, line_nb=line_nb)]) # open file with vscode

        """ if(self.text_editor == 'vscode'):
            arg = filename+':'+str(line_nb)
            subprocess.Popen(["code.cmd", "--goto", arg]) # open file with vscode
        elif(self.text_editor == 'sublime'):
            arg = filename+':'+str(line_nb)
            subprocess.Popen(["subl", arg]) # open file with vscode """
        # @trask
        # todo: implement other text editor calls (notepad, sublime, etc)

    def analyse_file(self, filename):
        ext = filename.split('.')[-1]
        if(ext == 'py'):
            trasks =  self.python_analyzer.inspect_file(filename)
            self.all_trasks.extend(trasks)
        else:
            print('unsupported file')

    def generate_single_id(self):
        i = 0
        for t in self.all_trasks:
            t.single_id = "trask_id_"+str(i)
            i += 1

    def get_trasks(self):
        # add single id for each trasks
        self.generate_single_id()
        return self.all_trasks

    def clear_trasks(self):
        self.all_trasks = []

    def on_refresh_btn(self):
        print("refresh btn pressed !")

    def on_test_btn(self):
        print("test btn")

    def on_locate_trask(self, filename, line_nb):
        self.open_file_at_line(filename, line_nb)

    def on_trask_moved(self, trask_id, source, dest):
        if(dest == 'todo_container'):
            new_type = 'todo'
        elif(dest == 'doing_container'):
            new_type = 'doing'
        elif(dest == 'done_container'):
            new_type = 'done'
        elif(dest == 'other_container'):
            new_type = 'other'
        
        for t in self.all_trasks:
            if(t.single_id == trask_id):
                t.modify_type(new_type)


# global
USE_FLASKWEBGUI = False

ux = AppUX()
app = Flask(__name__)
ui = FlaskUI(app)

# flask routing
@app.route("/")
def index():
    ux.clear_trasks()
    ux.analyse_file('sample_test_file.py')
    #ux.analyse_file('sample_test_file.py')
    trasks = ux.get_trasks()

    todo_trasks = [t for t in trasks if t.trask_type=='todo']
    doing_trasks = [t for t in trasks if t.trask_type=='doing']
    done_trasks = [t for t in trasks if t.trask_type=='done']
    other_trasks = [t for t in trasks if (t.trask_type!='todo' and t.trask_type!='doing' and t.trask_type!='done')]

    return render_template('ui.html', all_trasks=trasks, todo_trasks=todo_trasks, doing_trasks=doing_trasks, done_trasks=done_trasks, other_trasks=other_trasks)

#background process happening without any refreshing
@app.route('/background_process_test')
def background_process_test():
    ux.on_test_btn()
    return ("nothing")

@app.route('/background_locate')
def background_locate():
    filename = request.args.get('file', 0, type=str)
    line_nb = request.args.get('line', 0, type=int)
    print('locating {}:{}'.format(filename, line_nb))
    ux.on_locate_trask(filename, line_nb)
    return ("nothing")

@app.route('/trask_moved')
def trask_moved():
    trask_id = request.args.get('id', 0, type=str)
    source = request.args.get('from', 0, type=str)
    dest = request.args.get('dest', 0, type=str)
    print('Trask {} moved from {} to {}'.format(trask_id, source, dest))
    ux.on_trask_moved(trask_id, source, dest)
    return ("nothing")

def main(embedded=False, editor='vscode'): 
    ux.set_editor(editor)
    if(embedded):
        ui.run()
    else:
        app.run()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('-e', '--embedded', action='store_true', help="shows application in its own windows (versus flask web page)")
    parser.add_argument('-t', '--text-editor', dest='editor', help="Choice your editor between {}".format(list(supported_editor.keys())))

    args = parser.parse_args()
    if(args.embedded):
        main(True, args.editor)
    else:
        main(False, args.editor)


