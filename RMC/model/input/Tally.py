# -*- coding:utf-8 -*-
# author: Xiaoyu Guo

from RMC.model.input.base import YMLModelObject as BaseModel


class Tally(BaseModel):

    def __init__(self, meshtally=None, unparsed=''):
        if meshtally is None:
            meshtally = []

        self._meshtally = meshtally
        # todo 添加其他计数器选项的解析
        self._unparsed = unparsed

    @property
    def meshtally(self):
        return self._meshtally

    def check(self):
        pass

    def __str__(self):
        card = 'Tally\n'
        for meshtally in self._meshtally:
            card += str(meshtally)
        card += self._unparsed
        card += '\n\n'
        return card


class MeshTally(BaseModel):
    card_option_types = {
        'MESHTALLY': [int],  # id
        'TYPE': [int],
        'ENERGY': ['list', float, -1],
        'NORMALIZE': [int],
        'HDF5MESH': [int],
        'GEOMETRY': [int],
        'AXIS': ['list', float, 3],
        'VECTOR': ['list', float, 3],
        'ORIGIN': ['list', float, 3],
        'SCOPE': ['list', int, 3],
        'BOUND': ['list', float, 3],
        'SCOPEX': ['list', int, -1],
        'SCOPEY': ['list', int, -1],
        'SCOPEZ': ['list', int, -1],
        'BOUNDX': ['list', float, -1],
        'BOUNDY': ['list', float, -1],
        'BOUNDZ': ['list', float, -1],
    }

    def __init__(self, tally_id=1, tally_type=1, energy=None, normalize=0,
                 hdf5mesh=0, geometry=1,
                 axis=None, vector=None, origin=None,
                 scope=None, bound=None,
                 scopex=None, scopey=None, scopez=None,
                 boundx=None, boundy=None, boundz=None):
        self._id = tally_id
        self._type = tally_type
        self._energy = energy
        self._normalize = normalize
        self._hdf5mesh = hdf5mesh
        self._geometry = geometry
        self._axis = axis
        self._vector = vector
        self._origin = origin
        self._scope = scope
        self._bound = bound
        self._scopex = scopex
        self._scopey = scopey
        self._scopez = scopez
        self._boundx = boundx
        self._boundy = boundy
        self._boundz = boundz

    def add_options(self, options):
        if 'MESHTALLY' in options.keys():
            self._id = options['MESHTALLY']
        if 'TYPE' in options.keys():
            self._type = options['TYPE']
        if 'ENERGY' in options.keys():
            self._energy = options['ENERGY']
        if 'NORMALIZE' in options.keys():
            self._normalize = options['NORMALIZE']
        if 'HDF5MESH' in options.keys():
            self._hdf5mesh = options['HDF5MESH']
        if 'GEOMETRY' in options.keys():
            self._geometry = options['GEOMETRY']
        if 'AXIS' in options.keys():
            self._axis = options['AXIS']
        if 'VECTOR' in options.keys():
            self._vector = options['VECTOR']
        if 'ORIGIN' in options.keys():
            self._origin = options['ORIGIN']
        if 'SCOPE' in options.keys():
            self._scope = options['SCOPE']
        if 'BOUND' in options.keys():
            self._bound = options['BOUND']
        if 'SCOPEX' in options.keys():
            self._scopex = options['SCOPEX']
        if 'SCOPEY' in options.keys():
            self._scopey = options['SCOPEY']
        if 'SCOPEZ' in options.keys():
            self._scopez = options['SCOPEZ']
        if 'BOUNDX' in options.keys():
            self._boundx = options['BOUNDX']
        if 'BOUNDY' in options.keys():
            self._boundy = options['BOUNDY']
        if 'BOUNDZ' in options.keys():
            self._boundz = options['BOUNDZ']

    @property
    def scope(self):
        return self._scope

    @property
    def bound(self):
        return self._bound

    @property
    def scopex(self):
        return self._scopex

    @property
    def scopey(self):
        return self._scopey

    @property
    def scopez(self):
        return self._scopez

    @property
    def boundx(self):
        return self._boundx

    @property
    def boundy(self):
        return self._boundy

    @property
    def boundz(self):
        return self._boundz

    def check(self):
        assert self._id > 0
        assert self._type > 0

        if self._geometry == 2:
            assert self._axis is not None
            assert self._vector is not None
            assert self._origin is not None

        assert ((self._scope is None) == (self._bound is None) and
                (self._scopex is None) == (self._scopey is None) and
                (self._scopey is None) == (self._scopez is None) and
                (self._scopez is None) == (self._boundz is None) and
                (self._boundz is None) == (self._boundx is None) and
                (self._boundx is None) == (self._boundy is None) and
                (self._scope is None) != (self._scopex is None))

    def __str__(self):
        card = 'Meshtally'
        card += ' ' + str(self._id)
        card += ' type = ' + str(self._type)
        card += ' normalize = ' + str(self._normalize)
        card += ' hdf5mesh = ' + str(self._hdf5mesh)

        if self._energy is not None:
            card += ' energy =' + self._list_to_str(self._energy)

        if self._geometry != 1:
            card += ' geometry = ' + str(self._geometry)
            card += ' axis = ' + self._list_to_str(self._axis)
            card += ' vector = ' + self._list_to_str(self._vector)
            card += ' origin = ' + self._list_to_str(self._origin)

        if self._scope is not None:
            card += ' scope = ' + self._list_to_str(self._scope)
            card += ' bound = ' + self._list_to_str(self._bound)
        else:
            card += ' scopex = ' + self._list_to_str(self._scopex)
            card += ' scopey = ' + self._list_to_str(self._scopey)
            card += ' scopez = ' + self._list_to_str(self._scopez)
            card += ' boundx = ' + self._list_to_str(self._boundx)
            card += ' boundy = ' + self._list_to_str(self._boundy)
            card += ' boundz = ' + self._list_to_str(self._boundz)

        card += '\n'
        return card

    @staticmethod
    def _list_to_str(var_list):
        string = ''
        for e in var_list:
            string += ' ' + str(e)
        return string
