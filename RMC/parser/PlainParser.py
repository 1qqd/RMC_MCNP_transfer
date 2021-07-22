# -*- coding:utf-8 -*-
# author: Kaiwen Li
# date: 2019-11-16

import re
from RMC.modifier.formatter.PlainFormatter import PlainFormatter
from RMC.model.input.Geometry import *
from RMC.model.input.refuelling import *
from RMC.model.input.Include import IncludeMaterial
from RMC.model.input.Criticality import Criticality
from RMC.model.input.CriticalitySearch import CriticalitySearch
from RMC.model.input.Burnup import Burnup
from RMC.model.input.Print import Print
from RMC.model.input.Material import *
from RMC.model.input.Mesh import *
from RMC.model.input.Tally import *
from RMC.model.input.base import Model as InputModel


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
        for cards in self.content:
            # split block into single lines
            # example: UNIVERSE 1\nCell 1 -1:1 void=1
            #       to ["UNIVERSE 1", "Cell 1 -1:1 void=1"]
            cards = cards.strip('\n')
            card_list = cards.split('\n')
            card_title = card_list[0].split(' ', 2)
            card = card_title[0].upper()
            if card == 'INCLUDE':
                if (len(card_title) == 2) \
                        and (card_title[1].upper().startswith('MATERIAL')):
                    self.parsed_model.model['includematerial'] = \
                        IncludeMaterial(card_title[1])
                else:
                    self.parsed_model.model['unparsed'].append(cards)
                continue
            # currently only UNIVERSE block supports >= 2
            if len(card_title) >= 2:
                index = int(float(card_title[1]))
                options = ''
                # UNIVERSE with 'lattice', 'pitch', etc. options
                if len(card_title) >= 3:
                    options = card_title[2]

                if card == 'UNIVERSE':
                    univ = self._parse_universe(card_list[1:], int(index), options)
                    self.parsed_model.model['geometry'].add_universe(univ)
                else:
                    self.parsed_model.model['unparsed'].append(cards)
                    # raise ValueError('%s card with index can not be recognized!' % card)
            else:
                if card == 'REFUELLING':
                    refuel = self.__parse_refuelling(card_list[1:])
                    self.parsed_model.model['refuelling'] = refuel
                elif card == 'MATERIAL':
                    materialmodel = self.__parse_material(card_list[1:])
                    self.parsed_model.model['material'] = materialmodel
                elif card == 'CRITICALITY':
                    criticality = self.__parse_criticality(card_list[1:])
                    self.parsed_model.model['criticality'] = criticality
                elif card == 'BURNUP':
                    burnup = self.__parse_burnup(card_list[1:])
                    self.parsed_model.model['burnup'] = burnup
                elif card == 'CRITICALITYSEARCH':
                    criticalitysearch = self.__parse_criticalitysearch(card_list[1:])
                    self.parsed_model.model['criticalitysearch'] = criticalitysearch
                elif card == 'TALLY':
                    tallymodel = self.__parse_tally(card_list[1:])
                    self.parsed_model.model['tally'] = tallymodel
                elif card == 'PRINT':
                    printmodel = self.__parse_print(card_list[1:])
                    self.parsed_model.model['print'] = printmodel
                elif card == 'MESH':
                    meshmodel = self.__parse_mesh(card_list[1:])
                    self.parsed_model.model['mesh'] = meshmodel
                elif card == 'SURFACE':
                    surfmodel = self.__parse_surface(card_list[1:])
                    self.parsed_model.model['surface'] = surfmodel
                else:
                    self.parsed_model.model['unparsed'].append(cards)
                    # raise ValueError('%s card can not be recognized!' % card_list[0])

        self.parsed_model.postprocess()
        self._is_parsed = True
        return self.parsed_model

    @staticmethod
    def _parse_universe(content, index, options):
        univ = Universe(number=index)
        # if there are some options after the universe index.
        if options:
            options_val = PlainParser._parse_options(options, Universe.card_option_types)
            for opt in Universe.card_option_types.keys():
                if opt not in options_val:
                    options_val[opt] = None
            univ.add_options(options_val)

        # if there are cells in the universe.
        cells = []
        if len(content) > 0:
            for line in content:
                cells.append(PlainParser._parse_cell(line))
        univ.add_cells(cells)
        return univ

    @staticmethod
    def _parse_cell(content):
        options = content.split(' ', 2)
        if not options[0].upper() == 'CELL':
            raise ValueError('CELL options not found in %s' % content)
        # Get the index of the cell.
        index = int(float(options[1]))
        cell = Cell(number=index)

        # Delete the parsed part of the content.
        options = options[2].strip()

        # Get the bounds of the cell.
        cell_bounds_pattern = re.compile(r'^[^A-Za-z]+')
        m = cell_bounds_pattern.search(options)
        if not m:
            raise ValueError('Position definition not found in cell definition %s' % content)
        bounds = m.group(0)
        cell.add_bounds(bounds.strip())

        # Parse the remaining options of the cell.
        options_val = PlainParser._parse_options(options[len(bounds):], Cell.card_option_types)
        for opt in Cell.card_option_types.keys():
            if opt not in options_val:
                options_val[opt] = None
        cell.add_options(options_val)

        return cell

    @staticmethod
    def __parse_refuelling(content):
        file_option = None
        step_list = []
        for option in content:
            if option.split()[0].upper() == 'FILE':
                file_option = option
            elif option.split()[0].upper() == 'REFUEL':
                step_list = PlainParser._parse_options(option.split(' ', 1)[1], RefuelBlock.card_option_types)['STEP']
        if file_option is None or step_list is []:
            raise ValueError('FILE option not found in refuelling block.')
        opt_list = file_option.split(' ', 1)
        opt_list[0] = opt_list[0].upper()
        return RefuelBlock(file_name=opt_list[1].strip(), steps=step_list)

    @staticmethod
    def __parse_burnup(content):
        time_step = None
        burnup_step = None
        power = None
        powerden = None
        succession = None
        unparsed = ''
        for option in content:
            if option.split()[0].upper() == 'TIMESTEP':
                # option 不用 split是因为TIMESTEP卡中没有 m = n 这种形式
                time_step = PlainParser._parse_options(option, Burnup.card_option_types)['TIMESTEP']
            elif option.split()[0].upper() == 'BURNUPSTEP':
                burnup_step = PlainParser._parse_options(option, Burnup.card_option_types)['BURNUPSTEP']
            elif option.split()[0].upper() == 'POWER':
                power = PlainParser._parse_options(option, Burnup.card_option_types)['POWER']
            elif option.split()[0].upper() == 'POWERDEN':
                powerden = PlainParser._parse_options(option, Burnup.card_option_types)['POWERDEN']
            elif option.split()[0].upper() == 'SUCCESSION':
                succession = PlainParser._parse_options(option.split(' ', 1)[1], Burnup.card_option_types['SUCCESSION'])
            else:
                unparsed += option + '\n'
        if time_step is [] and burnup_step is []:
            raise ValueError('TIMESTEP or BURNUPSTEP option not found in BURNUP block.')
        if time_step and burnup_step:
            raise ValueError('TIMESTEP and BURNUPSTEP are repeatly defined in BURNUP block')
        if power is [] and powerden is []:
            raise ValueError('POWER or POWERDEN option not found in BURNUP block.')
        if power and powerden:
            raise ValueError('POWER and POWERDEN are repeatly defined in BURNUP block')
        return Burnup(time_step=time_step, burnup_step=burnup_step, power=power, power_den=powerden,
                      succession=succession, unparsed=unparsed)

    @staticmethod
    def __parse_criticality(content):
        max_iteration = None
        unparsed = ''
        for option in content:
            if option.split()[0].upper() == 'COUPLE':
                max_iteration = PlainParser._parse_options(option.split(' ', 1)[1],
                                                           Criticality.card_option_types)['MAXITERATION']
            else:
                unparsed += option + '\n'
        return Criticality(max_iteration=max_iteration, unparsed=unparsed)

    @staticmethod
    def __parse_criticalitysearch(content):
        unparsed = ''
        for option in content:
            unparsed += option + '\n'
        return CriticalitySearch(unparsed=unparsed)

    @staticmethod
    def __parse_material(content):
        unparsed = ''
        mats = []
        for option in content:
            if option.split()[0].upper() == 'MAT':
                mats.append(PlainParser.__parse_single_mat(option))
            else:
                unparsed += option + '\n'
        # mats.sort(key=id)
        return Materials(mats=mats, unparsed=unparsed)

    @staticmethod
    def __parse_single_mat(mat_card):
        opts = mat_card.split()
        mat = Material(mat_id=int(opts[1]), density=opts[2])

        i = 3
        while i < len(opts):
            mat.update_nuclide(Nuclide(opts[i], opts[i + 1]))
            i += 2

        return mat

    @staticmethod
    def __parse_surface(content):
        surfaces = []
        for option in content:
            surf_number = int(option.split(' ', 3)[1])
            surf_type = option.split(' ', 3)[2].upper()
            surf = PlainParser._parse_options(option.split(' ', 2)[2], Surface.surf_type_para)
            surf_parameter = surf[surf_type]
            if 'BC' in surf:
                surf_boundary = surf['BC']
            else:
                surf_boundary = None
            if 'PAIR' in surf:
                surf_pair = surf['PAIR']
            else:
                surf_pair = None
            surface = Surface(number=surf_number, stype=surf_type, parameters=surf_parameter, boundary=surf_boundary,
                              pair=surf_pair)
            surfaces.append(surface)
        return Surfaces(surfaces=surfaces)

    @staticmethod
    def __parse_mesh(content):
        meshmodel = Mesh()
        for option in content:
            mesh_options = PlainParser._parse_options(option, MeshInfo.card_option_types)
            meshinfocard = MeshInfo()
            meshinfocard.add_options(mesh_options)
            meshmodel.add_one_mesh(meshinfocard)
        return meshmodel

    @staticmethod
    def __parse_tally(content):
        unparsed = ''
        meshtally_list = []
        for option in content:
            if option.split()[0].upper() == 'MESHTALLY':
                opt_lst = PlainParser._parse_options(option, MeshTally.card_option_types)
                meshtally = MeshTally()
                meshtally.add_options(opt_lst)
                meshtally_list.append(meshtally)
            else:
                unparsed += option + '\n'
        return Tally(meshtally=meshtally_list, unparsed=unparsed)

    @staticmethod
    def __parse_print(content):
        unparsed = ''
        inpfile = 0
        for option in content:
            if option.split()[0].upper() == 'INPFILE':
                inpfile = PlainParser._parse_options(option, Print.card_option_types)['INPFILE']
            else:
                unparsed += option + '\n'
        return Print(inpfile=inpfile, unparsed=unparsed)

    @staticmethod
    def _parse_options(content, cards):
        options = content.replace(' = ', ' ').split()
        options_dict = {}
        while options:
            options[0] = options[0].upper()
            if options[0] in cards:
                dtype = cards[options[0]]
                if dtype[0] == 'list':
                    [opt_val, index] = PlainParser._parse_list(options, dtype[1])
                else:
                    [opt_val, index] = PlainParser._parse_val(options, dtype[0])

                options_dict[options[0]] = opt_val
                # 移除已经解析过的部分
                options = options[index:]
            else:
                raise ValueError('%s can not be recognized in %s.' % (options[0], content))
        return options_dict

    @staticmethod
    def _parse_list(options, func=str):
        index = 1
        opt_list = []
        while index < len(options):
            # 在燃耗中可以输入星号*，后面接一正整数n，表示重复n次
            if options[index] == '*':
                value = func(options[index - 1])
                # todo 容错处理，如用户输入 3 * 1.2，或者 * 前后不完整
                # todo RMC中的 * 有两种用途：一种表示重复次数，还有一种用在栅元计数器中，
                #  表示展开所有底层栅元。现在代码还没有处理第二种逻辑。
                # range里面 -1 是因为在读到 * 之前已经append过一次了
                for repeat in range(int(options[index + 1]) - 1):
                    opt_list.append(value)
                index += 2
            else:
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
