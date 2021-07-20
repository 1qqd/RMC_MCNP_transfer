# -*- coding:utf-8 -*-
# author: Xiaoyu Guo
# modifier: Kaiwen Li

import re


class PlainFormatter:
    def __init__(self, file_name):
        self.file_name = file_name
        self.content = ''
        self._s_changed = True
        self._formatted = False
        self._read = False

    def read(self):
        if self._read:
            return
        with open(self.file_name, 'r') as f:
            self.content = f.read()

    @property
    def changed(self):
        return self._s_changed

    def format(self):
        """
        function:
        0:add blanks around equals '=' and asterisks '*'
        1:delete all comment;
        2:trans all lower-case letters to upper-case letters;
        todo: Currently, 2 has been cancelled for some options are case-sensitive.
        3:delete all return character with a blank
          as the beginning of the next line;

        for input like this:
        UNIVERSE 11 move = 0 0 0  lat = 1  pitch = 1.26 1.26 1 scope = 17 17 1 fill=
         1  1  1
         1  1  1

        the output will be:
        UNIVERSE 11 MOVE = 0 0 0 LAT = 1 PITCH = 1.26 1.26 1 SCOPE = 17 17 1 FILL = 1  1  1  1  1  1
        :return: string after formatting
        """

        self.read()

        while self._s_changed:
            self._s_changed = False
            changed_inp = re.sub(r'[\t\r\f\v]', ' ', self.content)
            changed_inp = re.sub(r'(?P<char>[^ ])=', '\g<char> =', changed_inp)
            changed_inp = re.sub(r'=(?P<char>[^ ])', '= \g<char>', changed_inp)
            changed_inp = re.sub(r'(?P<char>[^ ])\*', '\g<char> *', changed_inp)
            changed_inp = re.sub(r'\*(?P<char>[^ ])', '* \g<char>', changed_inp)
            changed_inp = changed_inp.replace('  ', ' ')
            changed_inp = changed_inp.replace('\n\n\n', '\n\n')
            changed_inp = re.sub(r'[ ]+\n', '\n', changed_inp)
            # Remove the comments that occupy the whole line.
            # Note that even if the comment mark '//' is following some blanks,
            # this will not be regarded as a blank line.
            changed_inp = re.sub(r'\n[ ]*//[^\n]*\n', '\n', changed_inp)
            # Remove the variable definition
            changed_inp = re.sub(r'\n[ ]*@.*\n', '\n', changed_inp)
            # Remove the inline comments.
            changed_inp = re.sub(r'\n(?P<content>[ ]*[^ ]+.*?)//[^\n]*\n', '\n\g<content>\n', changed_inp)
            self._s_changed = (changed_inp != self.content)
            self.content = changed_inp

        # Remove the comment at the head and too many line-end signs at the end of the file.
        self.content = re.sub(r'^[ ]*//[^\n]*\n', '', self.content)
        self.content = re.sub(r'^[\n]+', '', self.content)
        self.content = re.sub(r'[\n]+$', '\n', self.content)
        self._formatted = True
        return self.content

    def format_and_output(self, output_file_name):
        """
        Format the file and write the formatted content into output_file_name file.
        :param output_file_name: the name of the file to be written.
        :return: None
        """
        if not self._formatted:
            self.format()
        with open(output_file_name, 'w') as f:
            f.write(self.content)

    def format_to_cards(self):
        if not self._formatted:
            self.format()

        # each card will be split into the element of a list.
        return self.content.replace('\n ', ' ').split('\n\n')

    def clear(self):
        self.content = ""
        self._formatted = False
        self._s_changed = True
        self._read = False
