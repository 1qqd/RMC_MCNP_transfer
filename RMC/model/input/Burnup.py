# -*- coding: utf-8 -*-
# author: Xiaoyu Guo

from RMC.model.input.base import YMLModelObject as BaseModel


# 注意：这里写的其实都是Block，包含的应该是keywords而不是options
class Burnup(BaseModel):
    card_option_types = {
        # 暂时只添加这几个option，因为不涉及修改其他的option
        'TIMESTEP': ['list', float, -1],
        'BURNUPSTEP': ['list', float, -1],
        'POWER': ['list', float, -1],
        'POWERDEN': ['list', float, -1],
        'SUCCESSION': {
            'POINTBURNUP': [bool],
            'SINGLESTEP': [bool],
            'FMF': [float],
            'CUMULATIVETIME': [float],
            'CUMULATIVEBURNUP': [float],
            'CELLCMLTVBURNUP': [bool]
        }
    }

    def __init__(self, time_step=None, burnup_step=None, power=None, power_den=None,
                 succession=None, unparsed=''):
        """

        :param time_step: 燃耗输入卡中的时间步
        :param power: 燃耗输入卡中的功率历史
        :param succession: 字典，里面有 'SINGLESTEP' 
               'POWER' 'TIMESTEP' 'POINTBURNUP'
        :param unparsed: 尚未被解析的部分
        """
        self._time_step = time_step
        self._burnup_step = burnup_step
        self._power = power
        self._power_den = power_den
        self._succession = succession
        self._single_step = 0
        if self._succession is not None:
            if 'SINGLESTEP' in self._succession:
                self._single_step = self._succession['SINGLESTEP']
        # 未解析的其他选项的字符串
        self._unparsed = unparsed

        self._current_step = 0

    def check(self):

        if self._time_step is [] and self._burnup_step is []:
            raise TypeError("one of TIMESTEP or BURNUPSTEP need to be provided")
        if self._time_step and self._burnup_step:
            raise TypeError("TIMESTEP and BURNUPSTEP are repeatly defined in BURNUP block")
        if self._power is [] and self._power_den is []:
            raise TypeError("One of POWER or POWERDEN need to be provided")
        if self._power and self._power_den:
            raise TypeError('POWER and POWERDEN are repeatly defined in BURNUP block')

        time_size = len(self._time_step) if self._time_step is not None else len(self._burnup_step)
        power_size = len(self._power) if self._power is not None else len(self._power_den)

        if time_size != power_size:
            raise ValueError("The number of POWER/POWERDEN is not equal to that of TIMESTEP/BURNUPSTEP")

    @property
    def step_number(self):
        time_size = len(self._time_step) if self._time_step else len(self._burnup_step)
        return time_size

    @property
    def current_step(self):
        return self._current_step

    @current_step.setter
    def current_step(self, current_step):
        self._current_step = current_step

    @property
    def single_step(self):
        return self._single_step

    @single_step.setter
    def single_step(self, single_step):
        self._single_step = single_step

    @property
    def power(self):
        return self._power

    @power.setter
    def power(self, p):
        self._power = p

    @property
    def power_den(self):
        return self._power_den

    @power_den.setter
    def power_den(self, pd):
        self._power_den = pd

    @property
    def succession(self):
        return self._succession

    @succession.setter
    def succession(self, succession):
        self._succession = succession

    @property
    def time_step(self):
        return self._time_step

    @time_step.setter
    def time_step(self, t):
        self._time_step = t

    @property
    def burnup_step(self):
        return self._burnup_step

    @burnup_step.setter
    def burnup_step(self, bs):
        self._burnup_step = bs

    def __str__(self):
        card = 'BURNUP\n'
        if self._time_step:
            card += 'TIMESTEP '
            for time in self._time_step:
                card += ' ' + str(time)
            card += '\n'
        if self._burnup_step:
            card += 'BURNUPSTEP '
            for burnup in self._burnup_step:
                card += ' ' + str(burnup)
            card += '\n'
        if self._power:
            card += 'POWER '
            for power in self._power:
                card += ' ' + str(power)
            card += '\n'
        if self._power_den:
            card += 'POWERDEN '
            for powerden in self._power_den:
                card += ' ' + str(powerden)
            card += '\n'
        if self._succession is not None:
            card += 'SUCCESSION'
            if self._single_step:
                card += ' SINGLESTEP = 1'
            if 'POINTBURNUP' in self._succession:
                if self._succession['POINTBURNUP']:
                    card += ' POINTBURNUP = 1'
            if 'FMF' in self._succession:
                card += ' FMF = ' + str(self._succession['FMF'])
            if 'CUMULATIVETIME' in self._succession:
                card += ' CUMULATIVETIME = ' + str(self._succession['CUMULATIVETIME'])
            if 'CUMULATIVEBURNUP' in self._succession:
                card += ' CUMULATIVEBURNUP = ' + str(self._succession['CUMULATIVEBURNUP'])
            if 'CELLCMLTVBURNUP' in self._succession:
                card += ' CELLCMLTVBURNUP = 1'
            card += '\n'
        if self._unparsed != '':
            card += self._unparsed
        card += '\n\n'
        return card
