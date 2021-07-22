# -*- coding:utf-8 -*-
# author: ShenPF
# date: 2021-07-20

import re
from MCNP.parser.PlainFormatter import PlainFormatter
from MCNP.model.base import Model as InputModel
from MCNP.model.Geometry import *


class PlainParser:
    def __init__(self, inp):
        self.inp = inp
        # block list
        self.content = ""
        self.parsed_model = InputModel()
        self._is_parsed = False

    def _read_in(self):
        converter = PlainFormatter(self.inp)
        self.content = converter.format_to_cards()
        converter.clear()

    def _prepare(self):
        self.parsed_model.model['geometry'] = Geometry()

    @property
    def parsed(self):
        if self._is_parsed:
            return self.parsed_model
        self._read_in()
        self._prepare()

        geometry_card = self.content[0]
        surface_card = self.content[1]

        if len(self.content) > 1:
            other_card = self.content[2]

