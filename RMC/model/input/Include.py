# -*- coding:utf-8 -*-
# author: Xiaoyu Guo

from RMC.model.input.base import YMLModelObject as BaseModel


class IncludeMaterial(BaseModel):
    card_option_types = {
        # 暂时不添加option
    }

    def __init__(self, material=''):
        self._material = material

    @property
    def material(self):
        return self._material

    def check(self):
        assert self._material != ''

    def __str__(self):
        card = 'INCLUDE ' + self._material + '\n\n'
        return card
