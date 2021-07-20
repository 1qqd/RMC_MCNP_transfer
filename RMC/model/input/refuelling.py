# -*- coding:utf-8 -*-
# author: Kaiwen Li
# date: 2019-11-15

from RMC.model.input.base import YMLModelObject as BaseModel


class RefuelBlock(BaseModel):
    card_option_types = {
        'FILE': [str],
        'STEP': ['list', int, -1]
    }

    def __init__(self, file_name=None, steps=None):
        self._file = file_name
        if steps is None:
            self.steps = []
        else:
            self.steps = steps

    def check(self):
        pass

    def __str__(self):
        card = 'REFUELLING\nFILE ' + self._file
        if len(self.steps) > 0:
            card += '\n'
            card += 'REFUEL step='
            for step in self.steps:
                card += ' ' + str(step)
        card += '\n\n'
        return card

    @property
    def file(self):
        return self._file


class Refuelling(BaseModel):
    yaml_tag = u'!refuelling'

    def __init__(self, lists=None):
        self.lists = lists

    def check(self):
        pass

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "%s(lists=%r)" % (self.__class__.__name__, self.lists)

    def __eq__(self, other):
        return repr(self) == repr(other)


class Refuel(BaseModel):
    yaml_tag = u'!do_refuel'

    def __init__(self, step=0, plan=None):
        self.step = step
        self.plan = plan

    def check(self):
        pass

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "%s(step=%r, plan=%r)" % (self.__class__.__name__, self.step, self.plan)


class RefuelPlan(BaseModel):
    yaml_tag = u'!refuel_univ'
    alia_name_list = ['column', 'row', 'new']

    def __init__(self, universe=0, position=None, alias=None, mapping=None):
        self.universe = universe
        self.position = position
        self.alias = alias
        self.mapping = mapping

    # todo: check the mapping, number, axis, etc.
    def check(self):
        pass

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "%s(universe=%r, position=%r, alias=%r, mapping=%r)" % (
            self.__class__.__name__, self.universe, self.position, self.alias, self.mapping
        )
