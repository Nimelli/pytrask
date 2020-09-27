from pathlib import Path

supported_languages = {
    'python':{
        'extension': ['py'],
        'single_line_comment_char': '#',
        'multi_line_comment_char_start': '"""',
        'multi_line_comment_char_stop': '"""'       
    },
    'c':{
        'extension': ['c', 'h'],
        'single_line_comment_char': '//',
        'multi_line_comment_char_start': '/*',
        'multi_line_comment_char_stop': '*/'       
    },    
}

class Trask():
    """"
    Trask Class:
    Define a Trask entity
    """
    def __init__(self, trask_type='None', author='', description=''):
        self.trask_type = trask_type
        self.author = author
        self.description = description
        self.tags = []
        self.in_file = None
        self.at_line = None
        self.single_id = None

    def construct_from_comment_str(self, comment, file, line):
        add_next_to = None

        self.in_file = file
        self.at_line = line

        for line in comment.split('\n'):

            words_list = [w for w in line.split(' ') if w!='']
            #print(words_list)
            for word in words_list:
                if('todo:' in word):
                    self.trask_type = 'todo'
                    add_next_to = 'description'

                elif('doing:' in word):
                    self.trask_type = 'doing'
                    add_next_to = 'description'

                elif('done:' in word):
                    self.trask_type = 'done'
                    add_next_to = 'description'

                elif('workaround:' in word):
                    self.trask_type = 'workaround'
                    add_next_to = 'description'

                elif('other:' in word):
                    self.trask_type = 'other'
                    add_next_to = 'description'

                elif('author:' in word):
                    add_next_to = 'author'

                elif('tag:' in word):
                    add_next_to = 'tag'

                elif(add_next_to == 'description'):
                    self.description += word + ' '

                elif(add_next_to == 'author'):
                    self.author = word
                    add_next_to = None

                elif(add_next_to == 'tag'):
                    if(len(word) > 0):
                        self.tags.append(word)

    def print(self):
        print('Trask in file {} @{}:'.format(self.in_file, self.at_line))
        print('Type: {}'.format(self.trask_type))
        print('author: {}'.format(self.author))
        print('description: {}'.format(self.description))
        print('tags: {}'.format(self.tags))

    def modify_type(self, new_type):
        print("Modifing trask type")
        if(new_type == self.trask_type):
            return

        to_change = self.trask_type + ':'
        to_change_by = new_type + ':'

        # open file and copy content
        with open(self.in_file, 'r') as in_file:
            content = in_file.readlines()

        for line_nb, line in enumerate(content):
            if(line_nb+1 > self.at_line):
                if(to_change in line):
                    # we found the line to change
                    old_line = line
                    new_line = old_line.replace(to_change, to_change_by)
                    content[line_nb] = new_line
                    break

        # write new content
        with open(self.in_file, 'w') as out_file:
            out_file.writelines(content)

        self.trask_type = new_type


class Analyzer():
    """"
    Analyzer Class:
    Object used to analyse a given file to retrieve its trasks
    """
    def __init__(self, language):
        self.supported_languages = supported_languages
        
        if(language in list(self.supported_languages.keys())):
            self.language = language
            self.single_line_comment_char = self.supported_languages[language]['single_line_comment_char']
            self.multi_line_comment_char_start = self.supported_languages[language]['multi_line_comment_char_start']
            self.multi_line_comment_char_stop = self.supported_languages[language]['multi_line_comment_char_stop']
            
        else:
            print('{} language not supported yet'.format(language))
            return ''

        self.multi_line_comment_started = False

    def extract_comment_from_line(self, line):
        if self.single_line_comment_char in line:
            return line.split(self.single_line_comment_char)[1]
        return ''

    def process_file_line(self, line):
        found = False
        end_of_multi_comment = False

        # check start of multi comment line
        if(not self.multi_line_comment_started and (self.multi_line_comment_char_start in line) ):
            self.multi_line_comment_started = True

        # check end of multi comment line
        elif(self.multi_line_comment_started and (self.multi_line_comment_char_stop in line) ):
            self.multi_line_comment_started = False
            end_of_multi_comment = True

        if('@trask' in line):
            # check if line is in a comment
            if(self.multi_line_comment_started):
                found = True
            elif(self.single_line_comment_char in line):
                found = True
            else:
                # not in a comment
                found = False
        else:
            found = False
            
        return (found, end_of_multi_comment)


    def inspect_file(self, filename):
        print("inspecting file: {}".format(filename))
        
        trasks = []

        with open(filename, 'r') as in_file:
            trask_comment_str = ''
            trask_found = False
            trask_found_at_line = None

            for line_nb, line in enumerate(in_file):

                (found, end_of_multi_comment) = self.process_file_line(line)
                if(found):
                    trask_found_at_line = line_nb+1
                    trask_found = True

                if(self.multi_line_comment_started):
                    # multi line comment analysis
                    trask_comment_str += line

                elif(trask_found and end_of_multi_comment):
                    trask_comment_str += line
                    new_trask = Trask()
                    new_trask.construct_from_comment_str(trask_comment_str, file=filename, line=trask_found_at_line)
                    trasks.append(new_trask)
                    trask_comment_str = ''
                    trask_found = False

                else:
                    # single line comment analysis
                    if(trask_found):
                        temp = self.extract_comment_from_line(line)

                        if(temp != ''):
                            trask_comment_str += temp
                        else:
                            new_trask = Trask()
                            new_trask.construct_from_comment_str(trask_comment_str, file=filename, line=trask_found_at_line)
                            trasks.append(new_trask)
                            trask_comment_str = ''
                            trask_found = False

        return trasks

class Trasker():
    """"
    Trasker Class:
    High-level object used to register files to be processed and to retreive all trasks.
    """
    def __init__(self):
        self.registered_files = []
        self.all_trasks = []
        self.supported_languages = supported_languages

    def register_file(self, filename):
        file = Path(filename)
        if(file.is_file()):
            # file exists
            self.registered_files.append(filename)
        else:
            print("{} not found".format(filename))

    def register_directory(self, directory, recursive=False):
        dir_path = Path(directory)
        if(dir_path.is_dir()):
            if(recursive):
                pathlist = Path(directory).glob('**/*.*')
            else:
                pathlist = Path(directory).glob('*.*')

            for path in pathlist:
                self.register_file(str(path))
        else:
            print("{} is not a valid directory path".format(directory))

    def analyse_file(self, filename):
        ext = filename.split('.')[-1]

        file_language = None
        for lang in self.supported_languages:
            if(ext in self.supported_languages[lang]['extension']):
                file_language = lang
                break

        if(file_language == None):
            print('Unsupported language for {}'.format(filename))
            return

        analyzer = Analyzer(language=file_language)
        trasks = analyzer.inspect_file(filename)
        self.all_trasks.extend(trasks)

    def analyse_all_files(self):
        for file in self.registered_files:
            self.analyse_file(file)

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


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--files', dest='files', nargs='+', help="Add path of files to analyse")
    parser.add_argument('-d', '--dir', dest='directory', help="Add path of directory to analyse")
    parser.add_argument('-r', '--rec', action='store_true', help="Make directory (-d) analisys recursive")

    args = parser.parse_args()

    trasker = Trasker()

    if(args.files != None):
        for file in args.files:
            trasker.register_file(file)

    if(args.directory != None):
        trasker.register_directory(args.directory, recursive=args.rec)

    trasker.analyse_all_files()
    trasks = trasker.get_trasks()

    print('Number trasks found: {}'.format(len(trasks)))
    for t in trasks:
        print('----------------------------')
        t.print()
