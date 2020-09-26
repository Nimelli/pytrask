
class Trask():
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
            self.single_line_comment_char = '#'
            self.multi_line_comment_char_start = '"""'
            self.multi_line_comment_char_stop = '"""'
            self.multi_line_comment_started = False
        else:
            print('{} language not supported yet'.format(language))
            return ''

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
            found = True
        else:
            found = False
            
        return (found, end_of_multi_comment)


    def inspect_file(self, filename):
        print("inspecting file: {}".format(filename))
        
        trasks = []

        with open(filename, 'r') as in_file:
            trask_comment_str = ''
            trask_found = False

            for line_nb, line in enumerate(in_file):

                (found, end_of_multi_comment) = self.process_file_line(line)
                if(found):
                    trask_found = True

                if(self.multi_line_comment_started):
                    # multi line comment analysis
                    trask_comment_str += line

                elif(end_of_multi_comment):
                    new_trask = Trask()
                    new_trask.construct_from_comment_str(trask_comment_str, file=filename, line=line_nb)
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
                            new_trask.construct_from_comment_str(trask_comment_str, file=filename, line=line_nb)
                            trasks.append(new_trask)
                            trask_comment_str = ''
                            trask_found = False

        return trasks



if __name__ == '__main__':
    in_filename = 'sample_test_file.py'

    analyzer = Analyzer()
    
    trasks = analyzer.inspect_file(in_filename)
    print('Number trasks found: {}'.format(len(trasks)))
    for t in trasks:
        print('----------------------------')
        t.display()
