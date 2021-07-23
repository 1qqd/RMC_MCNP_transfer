# -*- coding:utf-8 -*-
# author: Shen PF
# date: 2021-07-20

from MCNP.model.base import YMLModelObject as BaseModel
import numpy as np


class Cell(BaseModel):
    yaml_tag = u'!cell'
    card_option_types = {
        'FILL': [int],
        'U': [int],
        'LAT': [int],
        'TRCL': [int],
        'INNER': [bool],
        'IMP:N': [float]
    }

    def __init__(self, number=-1, bounds='', material=None, density=None, fill=None, inner=False, u=0, lat=None,
                 unparsed=None, impn=None):
        self.number = number
        self.bounds = bounds
        self.fill = fill
        self.inner = inner
        self.material = material
        self.density = density
        self.universe = u
        self.lat = lat
        self.unparsed = unparsed
        self.impn = impn

    def check(self):
        assert self.number >= 0

    def add_bounds(self, bounds):
        self.bounds = bounds
        pass

    def add_options(self, options):
        if 'FILL' in options.keys():
            self.fill = options['FILL']
        if 'U' in options.keys():
            self.universe = options['U']
        if 'LAT' in options.keys():
            self.lat = options['LAT']
        if 'IMP:N' in options.keys():
            self.impn = options['IMP:N']

    def __str__(self):
        s = '%d %d ' % (self.number, self.material)
        if self.density is not None:
            s += '%f ' % self.density
        else:
            s += '         '
        s += self.bounds + ' '
        if self.fill is not None:
            s += 'fill=%d ' % self.fill
        if self.universe != 0:
            s += 'u=%d ' % self.universe
        if self.lat is not None:
            s += 'lat=%d ' % self.lat
        s += '\n'
        if self.unparsed is not None and self.unparsed != '':
            s += ' Warning: No parserd options : ' + self.unparsed + '\n'
        return s


class Geometry(BaseModel):
    yaml_tag = u'!geometry'

    def __init__(self, universes=None, cell_dict=None, cells=None, unparsed=None):
        if universes is None:
            universes = []
        self.universes = universes
        self.univ_dict = {}
        if cells is None:
            cells = []
        self.cells = cells
        if cell_dict:
            cell_dict = {}
        self.cell_dict = cell_dict
        self.unparsed = unparsed

    def check(self):
        assert len(self.universes) > 0

    def add_universe(self, univ):
        self.universes.append(univ)

    def get_univ(self, uid):
        return self.univ_dict[uid]

    def get_cell(self, cid):
        return self.cell_dict[cid]

    def __str__(self):
        s = ''
        for cell in self.cells:
            s += str(cell)
        if self.unparsed is not None and self.unparsed != '':
            s += 'Warning: No parsed cells in geometry block:\n' + self.unparsed
        s += '\n\n'
        return s

    def __iter__(self):
        for univ in self.universes:
            yield univ


class Surfaces(BaseModel):
    yaml_tag = u'!surfaces'

    def __init__(self, surfaces=None, unparsed=''):
        self.surfaces = surfaces
        if self.surfaces is None:
            self.surfaces = []
        self.unparsed = unparsed

    def check(self):
        pass

    def find_surf(self, predicate):
        try:
            return next(idx for idx, n in enumerate(self.surfaces) if predicate(n.number))
        except StopIteration:
            return None

    def update_surface(self, old_surf, new_surf):
        surf_pos = self.find_surf(lambda x: x == old_surf.number)
        if surf_pos is not None:
            assert self.surfaces[surf_pos].type == new_surf.type
            self.surfaces[surf_pos].parameters = new_surf.parameters
        else:
            raise ValueError(
                f'The old surface {old_surf.number} is not in Surfaces of input\n')

    def add_surface(self, surface):
        surf_pos = self.find_surf(lambda x: x == surface.number)
        if surf_pos is None:
            self.surfaces.append(surface)
        else:
            raise ValueError(
                f'The new surface {surface.number} is already in Surfaces of input\n')

    def get_surface(self, surf_num):
        surf_pos = self.find_surf(lambda x: x == surf_num)
        if surf_pos is not None:
            return self.surfaces[surf_pos]
        else:
            raise ValueError(
                f'The surface {surf_num} is not in Surfaces of input')

    def __str__(self):
        s = ''
        for surf in self.surfaces:
            s += str(surf)
        if self.unparsed:
            s += 'Warning: No parsed cards in Surface block: \n' + self.unparsed
        s += '\n\n'
        return s


class Surface(BaseModel):
    yaml_tag = u'!surface'

    surf_type_para = {
        'P': ['list', float, 4],
        'PX': [float],
        'PY': [float],
        'PZ': [float],
        'SO': [float],
        'S': ['list', float, 4],
        'SX': ['list', float, 2],
        'SY': ['list', float, 2],
        'SZ': ['list', float, 2],
        'C/X': ['list', float, 3],
        'C/Y': ['list', float, 3],
        'C/Z': ['list', float, 3],
        'CX': [float],
        'CY': [float],
        'CZ': [float],
        'K/X': ['list', float, 5],
        'K/Y': ['list', float, 5],
        'K/Z': ['list', float, 5],
        'KX': ['list', float, 5],
        'KY': ['list', float, 5],
        'KZ': ['list', float, 5],
        'SQ': ['list', float, 10],
        'GQ': ['list', float, 10],
        'TX': ['list', float, 6],
        'TY': ['list', float, 6],
        'TZ': ['list', float, 6],
        # only for boundary condition
        'BC': [int],
        'PAIR': [int]
    }

    def __init__(self, number=None, stype=None, parameters=None, boundary=None, pair=None, unparsed=None):
        self.number = number
        self.type = stype
        self.parameters = parameters
        self.boundary = boundary
        self.pair = pair
        self.unparsed = unparsed

    def check(self):
        assert self.number >= 0

    def __str__(self):
        card = str(self.number) + ' ' + self.type + ' '
        surf_para = ' '.join([str(x) for x in self.parameters]) if isinstance(self.parameters, list) else ' ' + str(
            self.parameters)
        card += surf_para
        card += '\n'
        if self.unparsed:
            card += self.unparsed + '\n'
        return card
