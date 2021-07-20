# -*- coding: utf-8 -*-
# author: Xiaoyu Guo

from RMC.model.input.base import YMLModelObject as BaseModel


class Criticality(BaseModel):
    card_option_types = {
        # todo 完善各类选项
        'MAXITERATION': [int],
    }

    def __init__(self, max_iteration=None, unparsed=''):
        self._max_iteration = max_iteration
        self._unparsed = unparsed

        self.couple_option = False
        if self._max_iteration is not None:
            self.couple_option = True

    def check(self):
        if self._max_iteration is not None:
            assert self._max_iteration >= 1

    @property
    def max_iteration(self):
        return self._max_iteration

    @max_iteration.setter
    def max_iteration(self, max_iteration):
        self._max_iteration = max_iteration

    def __str__(self):
        card = 'CRITICALITY\n'
        if self._unparsed != '':
            card += self._unparsed
        # 注意：max_iteration选项不会输出，因为RMC不需要读取这个选项
        card += '\n\n'
        return card
