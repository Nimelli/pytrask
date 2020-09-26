
class Trask():
    def __init__(self, trask_type='todo', author='', description=''):
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
            for idx, word in enumerate(words_list):
                if(idx == 0): # first word
                    if('todo' in word):
                        self.trask_type = 'todo'
                        add_next_to = 'description'

                    elif('doing' in word):
                        self.trask_type = 'doing'
                        add_next_to = 'description'

                    elif('done' in word):
                        self.trask_type = 'done'
                        add_next_to = 'description'

                    elif('workaround' in word):
                        self.trask_type = 'workaround'
                        add_next_to = 'description'

                    elif('author' in word):
                        add_next_to = 'author'

                    elif('tag' in word):
                        add_next_to = 'tag'

                else:
                    if(add_next_to == 'description'):
                        self.description += word + ' '

                    elif(add_next_to == 'author'):
                        self.author = word
                        add_next_to = None

                    elif(add_next_to == 'tag'):
                        if(len(word) > 0):
                            self.tags.append(word)

    def display(self):
        print('Trask in file {} @{}:'.format(self.in_file, self.at_line))
        print('Type: {}'.format(self.trask_type))
        print('author: {}'.format(self.author))
        print('description: {}'.format(self.description))
        print('tags: {}'.format(self.tags))


class Analyzer():
    def __init__(self, language='python'):
        
        if(language == 'python'):
            self.language = language
            self.comment_char = '#'
        else:
            print('{} language not supported yet'.format(language))
            return ''

    def extract_comment_from_line(self, line):
        if self.comment_char in line:
            return line.split('#')[1]
        return ''

    def inspect_file(self, filename):
        print("inspecting file: {}".format(filename))
        
        trasks = []

        with open(filename, 'r') as in_file:
            trask_comment_str = ''
            found = False
            for line_nb, line in enumerate(in_file):

                if('@trask' in line):
                    found = True
                    trask_comment_str = line

                elif(found):
                    temp = self.extract_comment_from_line(line)
                    if(temp != ''):
                        trask_comment_str += temp
                    else:
                        found = False
                        #print(trask_comment_str)

                        new_trask = Trask()
                        new_trask.construct_from_comment_str(trask_comment_str, file=filename, line=line_nb)
                        trasks.append(new_trask)

        # generate single id for all trasks
        i = 0
        for t in trasks:
            t.single_id = "trask_id_"+str(i)
            i += 1

        return trasks



if __name__ == '__main__':
    import time
    in_filename = 'sample_test_file.py'

    analyzer = Analyzer()

    try:
        while(True):
            trasks = analyzer.inspect_file(in_filename)
            print('Number trasks found: {}'.format(len(trasks)))
            for t in trasks:
                print('----------------------------')
                t.display()

            time.sleep(1)
    except KeyboardInterrupt:
        print('terminated')
