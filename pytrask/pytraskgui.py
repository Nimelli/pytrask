from flask import Flask, render_template, request

#from trasker import Trask, Analyzer
from pytrask.trasker import Trask, Trasker


import subprocess
from flaskwebgui import FlaskUI

from pathlib import Path

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
        self.text_editor = 'vscode' #by default
        self.all_trasks = []

    def set_editor(self, editor):
        if editor in list(supported_editor.keys()):
            self.text_editor = editor

    def open_file_at_line(self, filename, line_nb):

        app = supported_editor[self.text_editor]['app']
        cmd = supported_editor[self.text_editor]['cmd']
        arg = supported_editor[self.text_editor]['arg']

        try:
            subprocess.Popen([app, cmd, arg.format(filename=filename, line_nb=line_nb)]) # open file with vscode
        except:
            print("Couldn't open the file. Current supported platform is Windows with the following backend editor: {}".format(list(supported_editor.keys())))
            # @trask
            # todo: add support for more text editor, and more platform (MAC, Linux)
    
    def on_refresh_btn(self):
        print("refresh btn pressed !")

    def on_test_btn(self):
        print("test btn")

    def on_locate_trask(self, trask_id):
        filename = None
        line_nb = 0
        for t in self.all_trasks:
            if(t.single_id == trask_id):
                filename = t.in_file
                line_nb = t.at_line
                break
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
trasker = Trasker()
app = Flask(__name__)
ui = FlaskUI(app)

# flask routing
@app.route("/")
def index():
    trasker.clear_trasks()
    trasker.analyse_all_files()
    trasks = trasker.get_trasks()
    ux.all_trasks = trasks

    todo_trasks = [t for t in trasks if t.trask_type=='todo']
    doing_trasks = [t for t in trasks if t.trask_type=='doing']
    done_trasks = [t for t in trasks if t.trask_type=='done']
    other_trasks = [t for t in trasks if (t.trask_type!='todo' and t.trask_type!='doing' and t.trask_type!='done')]

    editors = list(supported_editor.keys())

    return render_template('ui.html', all_trasks=trasks, todo_trasks=todo_trasks, doing_trasks=doing_trasks, done_trasks=done_trasks, other_trasks=other_trasks, editors=editors)

#background process happening without any refreshing
@app.route('/update_editor')
def update_editor():
    editor = request.args.get('editor', 0, type=str)
    print('update editor: {}'.format(editor))
    ux.set_editor(editor)
    return ("nothing")

@app.route('/background_locate')
def background_locate():
    trask_id = request.args.get('id', 0, type=str)
    print('locating {}'.format(trask_id))
    ux.on_locate_trask(trask_id)
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
    parser.add_argument('-t', '--text-editor', dest='editor', help="Choose which editor will open your trasks: {}. Default is vscode".format(list(supported_editor.keys())))
    parser.add_argument('-f', '--files', dest='files', nargs='+', help="Add path of files to analyse")
    parser.add_argument('-d', '--dir', dest='directory', default='.', help="Add path of directory to analyse")
    parser.add_argument('-nr', '--non-recursive', dest='nonrecursive', action='store_true', help="Make directory (-d) analisys non-recursive, recursive by default")

    args = parser.parse_args()

    if(args.files != None):
        for file in args.files:
            trasker.register_file(file)

    elif(args.directory != None):
        recursive = not args.nonrecursive
        trasker.register_directory(args.directory, recursive=recursive)

    if(args.embedded):
        main(True, args.editor)
    else:
        main(False, args.editor)


