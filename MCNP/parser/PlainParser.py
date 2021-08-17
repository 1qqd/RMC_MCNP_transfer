# -*- coding:utf-8 -*-
# author: ShenPF
# date: 2021-07-20

import re
import copy
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

    @property
    def parsed(self):
        if self._is_parsed:
            return self.parsed_model
        self._read_in()

        geometry_card = self.content[0].split('\n')
        surface_card = self.content[1].split('\n')

        [cells, geom_unparsed] = self.__parse_geometry(geometry_card)
        geometry_model = Geometry(cells=cells, unparsed=geom_unparsed)
        surface_model = self.__parse_surface(surface_card)

        self.parsed_model.model['surface'] = surface_model
        self.parsed_model.model['geometry'] = geometry_model

        if len(self.content) > 1:
            other_card = self.content[2]
            other_cards = self.split_othercard(other_card)
            mat_card = other_cards[0]
            material_model = self.__parse_material(mat_card)
            self.parsed_model.model['materials'] = material_model
            self.parsed_model.model['unparsed'] = other_cards[1]

        return self.parsed_model

    @staticmethod
    def split_othercard(other_card):
        lines = other_card.split('\n')
        mat_lines = []
        un_parsed = []
        for line in lines:
            words = line.split(' ')
            if re.match(r'm[1-9]+', words[0], re.I):
                mat_lines.append(line)
            elif re.match(r'mt[1-9]+', words[0], re.I):
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
            surf_boundary = None
            surf_unparsed = ''
            reflect_match = re.match(r'\*', option)
            if reflect_match:
                surf_boundary = 2
                option = option[1:]
            surf_match = re.match(r'([0-9]+) ', option)
            words = option.split()
            if surf_match:
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
                if surf_type in Surface.surf_type_para:
                    [surf, unpar] = PlainParser._parse_option(other_vars, Surface.surf_type_para)
                    if unpar is not '':
                        surf_unparsed += 'Warning: No parsed card: ' + str(unpar) + ' '
                    surface = Surface(number=surf_id, stype=surf_type, parameters=surf[surf_type],
                                      boundary=surf_boundary, pair=surf_pair, unparsed=surf_unparsed)
                    surfaces.append(surface)
                else:
                    unparsed += option + '\n'
            else:
                unparsed += option + '\n'

        return Surfaces(surfaces=surfaces, unparsed=unparsed)

    @staticmethod
    def __parse_geometry(content):
        cells = []
        universes = []
        geo_unparsed = ''
        for cell in content:
            cell_len = len(cell.split())
            cell_id = int(cell.split()[0])
            unparsed = ''

            if cell.split()[1].upper() != 'LIKE':  # like 'j m d geom params'
                index = 0
                mat_id = int(cell.split()[1])
                mat_density = None
                if mat_id == 0:
                    index = 2
                else:
                    index = 3
                    mat_density = float(cell.split()[2])
                cell_geom = ''
                geom_no_end = True
                while geom_no_end:
                    options = cell.split()[index:]
                    for param in Cell.card_option_types:
                        if re.match(param, options[0], re.I):
                            geom_no_end = False
                            break
                    if not geom_no_end:
                        break
                    if options[0] is ':':
                        cell_geom = cell_geom[0:len(cell_geom)-1]
                        cell_geom += options[0]
                    else:
                        cell_geom += '(' + options[0] + ')' + '&'
                    index += 1
                    if index >= cell_len:
                        geom_no_end = False
                        break

                cell_geom = cell_geom[0:len(cell_geom) - 1]
                cell_dict = {}
                cell_card_options = copy.deepcopy(Cell.card_option_types)
                if index != cell_len:
                    unparsed_items = ' '.join(cell.split()[index:])
                    while unparsed_items is not '':
                        if 'LAT' in cell_dict and 'FILL' in cell_card_options:
                            cell_card_options.pop('FILL')
                        [cell_dict_item, unparsed_items_new] = PlainParser._parse_option(unparsed_items,
                                                                                         cell_card_options)
                        if cell_dict_item:
                            cell_dict[unparsed_items.split()[0].upper()] = cell_dict_item[
                                unparsed_items.split()[0].upper()]
                        if unparsed_items_new is '':
                            unparsed_items = unparsed_items_new
                        elif unparsed_items.split()[0] == unparsed_items_new.split()[0]:
                            unparsed += ' ' + unparsed_items.split()[0]
                            unparsed_items = ' '.join(unparsed_items.split()[1:])
                        else:
                            unparsed_items = unparsed_items_new

                parsed_cell = Cell(cell_id, material=mat_id, density=mat_density, bounds=cell_geom, unparsed=unparsed)
                parsed_cell.add_options(cell_dict)
                cells.append(parsed_cell)

            else:  # like 'j LIKE n BUT list'
                geo_unparsed += cell + '\n'
        return [cells, geo_unparsed]

    @staticmethod
    def _parse_option(content, cards):
        options = content.replace(' = ', ' ').split()
        options_dict = {}
        unparsed = []
        index = 0
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
