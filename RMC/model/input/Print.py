# -*- coding: utf-8 -*-
# author: Xiaoyu Guo

from RMC.model.input.base import YMLModelObject as BaseModel


class Print(BaseModel):
    card_option_types = {
        # todo 完善各类选项
        'INPFILE': [int],
    }

    def __init__(self, inpfile=0, unparsed=''):
        self._inpfile = inpfile
        self._unparsed = unparsed

    def check(self):
        assert self._inpfile >= 0

    @property
    def inpfile(self):
        return self._inpfile

    @inpfile.setter
    def inpfile(self, inpfile):
        self._inpfile = inpfile

    def __str__(self):
        card = 'PRINT\n'
        card += 'inpfile ' + str(self._inpfile) + '\n'
        if self._unparsed != '':
            card += self._unparsed
        card += '\n\n'
        return card
