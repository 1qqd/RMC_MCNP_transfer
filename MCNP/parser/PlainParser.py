# -*- coding:utf-8 -*-
# author: ShenPF
# date: 2021-07-20

import re
from MCNP.parser.PlainFormatter import PlainFormatter
from MCNP.model.base import Model as InputModel
from MCNP.model.Geometry import *
from MCNP.model.Material import *


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

        geometry_card = self.content[0].split('\n')
        surface_card = self.content[1].split('\n')

        if len(self.content) > 1:
            other_card = self.content[2]
            other_cards = self.split_othercard(other_card)
            mat_card = other_cards[0]
            materialmodel = self.__parse_material(mat_card)
            self.parsed_model.model['material'] = materialmodel

        test = str(materialmodel)

        pass


    def split_othercard(self, other_card):
        lines = other_card.split('\n')
        mat_lines = []
        un_parsed = []
        for line in lines:
            words = line.split(' ')
            if re.match(r'm[1-9]+', words[0]):
                mat_lines.append(line)
            elif re.match(r'mt[1-9]+', words[0]):
                mat_lines.append(line)
            else:
                un_parsed.append(line)
        return [mat_lines, un_parsed]

    @staticmethod
    def __parse_material(content):
        unparsed = ''
        mats = []
        mts = []
        for option in content:
            if re.match(r'm[1-9]+', option, re.I):
                mats.append(PlainParser.__parse_single_mat(option))
            elif re.match(r'mt[1-9]+', option, re.I):
                words = option.split()
                mt_id = int(words[0][2:])
                mts.append(Mt(id=mt_id, name=words[1]))
            else:
                unparsed += option + '\n'
        return Materials(mats=mats, mts=mts, unparsed=unparsed)

    @staticmethod
    def __parse_single_mat(mat_card):
        opts = mat_card.split()
        mat = Material(mat_id=int(opts[0][1:]))

        i = 1
        while i < len(opts):
            mat.update_nuclide(Nuclide(opts[i], opts[i + 1]))
            i += 2

        return mat
