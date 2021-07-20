# -*- coding: utf-8 -*-
# author: Xiaoyu Guo

from RMC.model.input.base import YMLModelObject as BaseModel


class CriticalitySearch(BaseModel):
    # todo 添加详细的参数解析功能
    card_option_types = {
    }

    def __init__(self, unparsed=''):
        self._unparsed = unparsed

    def check(self):
        assert self._unparsed != ''

    def __str__(self):
        card = 'CRITICALITYSEARCH\n'
        if self._unparsed != '':
            card += self._unparsed
        card += '\n\n'
        return card
