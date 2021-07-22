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
        self._special_define_processed = True

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
            changed_inp = re.sub(r'\n[ ]*[cC][^\n]*\n', '\n', changed_inp)
            # Remove the inline comments.
            changed_inp = re.sub(r'\n(?P<content>[ ]*[^ ]+.*?)\$[^\n]*\n', '\n\g<content>\n', changed_inp)
            changed_inp = re.sub(r'(?P<front>[0-9\.]+)-(?P<back>[0-9]+)', '\g<front>e-\g<back>', changed_inp)
            self._s_changed = (changed_inp != self.content)
            self.content = changed_inp

        # Remove the comment at the head and too many line-end signs at the end of the file.
        self.content = re.sub(r'.*\n', '', self.content, count=1)  # remove the first line
        self.content = re.sub(r'^[\n]+', '', self.content)
        self.content = re.sub(r'[\n]+$', '\n', self.content)

        changed_inp = self.content
        while self._special_define_processed:  # process the %d nR / ni / nm pattern
            self._special_define_processed = False

            reg = r'([0-9\.]+) ([1-9]*)[Rr]'   # like '2 4R'
            searched = re.search(reg, changed_inp)
            if searched:
                rep_index = list(searched.span())
                rep_str = searched.group()
                rep_str1 = searched.group(1)
                if searched.group(2) == '':
                    rep_str2 = 1
                else:
                    rep_str2 = int(searched.group(2))  # '4'
                rep_new = rep_str1
                for i in range(rep_str2):
                    rep_new += ' ' + rep_str1
                changed_inp = self.replace_string(changed_inp, rep_index, rep_new)
                self._special_define_processed = (changed_inp != self.content)
                continue

            reg = r'([0-9\.]+) ([1-9]*)[Ii] ([0-9\.]+)'  # like '1 4I 6'
            searched = re.search(reg, changed_inp)
            if searched:
                rep_index = list(searched.span())
                rep_str = searched.group()
                rep_str1 = float(searched.group(1))  # '1'
                if searched.group(2) == '':
                    rep_str2 = 1
                else:
                    rep_str2 = int(searched.group(2))  # '4'
                rep_str3 = float(searched.group(3))  # '6'
                internal = (rep_str3-rep_str1)/(rep_str2+1)
                rep_new = str(rep_str1)
                for i in range(rep_str2+1):
                    rep_new += ' ' + str(rep_str1 + (i+1)*internal)
                changed_inp = self.replace_string(changed_inp, rep_index, rep_new)
                self._special_define_processed = (changed_inp != self.content)
                continue

            reg = r'([0-9\.]+) ([1-9\.]+)[Mm]'  # like '2 4m'
            searched = re.search(reg, changed_inp)
            if searched:
                rep_index = list(searched.span())
                rep_str = searched.group()
                rep_str1 = float(searched.group(1))
                rep_str2 = float(searched.group(2))
                rep_new = str(rep_str1) + ' ' + str(rep_str1*rep_str2)
                changed_inp = self.replace_string(changed_inp, rep_index, rep_new)
                self._special_define_processed = (changed_inp != self.content)
                continue

        self.content = changed_inp
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
        cards = self.content.split('\n\n')

        lines = cards[0].split('\n')
        cards[0] = '\n'.join([line.strip() for line in lines])
        lines = cards[1].split('\n')
        cards[1] = '\n'.join([line.strip() for line in lines])
        self.content = '\n\n'.join(cards)
        # each card will be split into the element of a list.
        return self.content.replace('\n ', ' ').split('\n\n')

    def clear(self):
        self.content = ""
        self._formatted = False
        self._s_changed = True
        self._read = False

    def replace_string(self, content, indexlist, strnew):
        length = len(content)
        contentlist = list(content)
        newlist = contentlist[0:indexlist[0]] + list(strnew) + contentlist[indexlist[1]:length]
        return ''.join(newlist)

    def sub_string(self, content, indexlist, strold, strnew):
        length = len(content)
        listcont = list(content)
        startstr = ''.join(listcont[0:indexlist[0]])
        substr = ''.join(listcont[indexlist[0]:indexlist[1]])
        remainstr = ''.join(listcont[indexlist[1]:length])

        substr = re.sub(r'(?P<start>[^a-zA-Z0-9_]+?)' + strold + r'(?P<end>[^a-zA-Z0-9_]+?)', r'\g<start>'+strnew+r'\g<end>', substr)

        return startstr + substr + remainstr