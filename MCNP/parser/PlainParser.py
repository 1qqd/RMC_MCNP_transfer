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

        surface_model = self.__parse_surface(surface_card)

        test = str(materialmodel)
        test2 = str(surface_model)

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

    @staticmethod
    def __parse_surface(content):
        surfaces = []
        unparsed = ''
        for option in content:
            words = option.split()
            surf_unparsed = ''
            surf_match = re.match(r'([0-9]+) ', option)
            if surf_match:
                surf_boundary = None
                surf_pair = None
                surf_id = int(words[0])
                if re.match(r'[0-9\+\-]+', words[1]):
                    var = int(words[1])
                    if var < 0:
                        surf_boundary = 3  # 周期边界条件
                        surf_pair = abs(var)
                    if var > 0:
                        surf_unparsed += 'Warning: No processed transformation id ' + str(var) + ' for Surface ' + str(
                            surf_id) + ' '
                    surf_type = words[2].upper()
                    other_vars = ' '.join(words[2:])
                else:
                    surf_type = words[1].upper()
                    other_vars = ' '.join(words[1:])
                [surf, unpar] = PlainParser._parse_options(other_vars, Surface.surf_type_para)
                if unpar is not '':
                    surf_unparsed += 'Warning: No parsed card: ' + str(unpar) + ' '
                surface = Surface(number=surf_id, stype=surf_type, parameters=surf[surf_type],
                                  boundary=surf_boundary, pair=surf_pair, unparsed=surf_unparsed)
                surfaces.append(surface)
            else:
                unparsed += option + '\n'

        return Surfaces(surfaces=surfaces, unparsed=unparsed)

    @staticmethod
    def _parse_options(content, cards):
        options = content.replace(' = ', ' ').split()
        options_dict = {}
        unparsed = []
        if options:
            options[0] = options[0].upper()
            if options[0] in cards:
                dtype = cards[options[0]]
                if dtype[0] == 'list':
                    [opt_val, index] = PlainParser._parse_list(options, dtype[1])
                else:
                    [opt_val, index] = PlainParser._parse_val(options, dtype[0])

                options_dict[options[0]] = opt_val
                # 移除已经解析过的部分
                unparsed = ' '.join(options[index:])
            else:
                raise ValueError('%s can not be recognized in %s.' % (options[0], content))
        return [options_dict, unparsed]

    @staticmethod
    def _parse_list(options, func=str):
        index = 1
        opt_list = []
        while index < len(options):
            try:
                value = func(options[index])
                index += 1
                opt_list.append(value)
            except ValueError:
                break
        # todo: check
        return [opt_list, index]

    @staticmethod
    def _parse_val(options, func=str):
        if func == bool:
            return [func(float(options[1])), 2]
        elif func == int:  # 二院项目要求智能识别int和float
            return [func(float(options[1])), 2]
        else:
            return [func(options[1]), 2]
