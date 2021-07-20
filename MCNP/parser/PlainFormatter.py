# -*- coding:utf-8 -*-
# author: Shen PF
# date: 2021-07-20

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
            # Note that even if the comment mark 'c' is following some blanks,
            # this will not be regarded as a blank line.
            changed_inp = re.sub(r'\n[ ]*c[^\n]*\n', '\n', changed_inp)
            # Remove the inline comments.
            changed_inp = re.sub(r'\n(?P<content>[ ]*[^ ]+.*?)\$[^\n]*\n', '\n\g<content>\n', changed_inp)
            self._s_changed = (changed_inp != self.content)
            self.content = changed_inp

        # Remove the comment at the head and too many line-end signs at the end of the file.
        self.content = re.sub(r'.*\n', '', self.content, count=1)  # remove the first line
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
