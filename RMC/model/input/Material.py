# -*- coding: utf-8 -*-
# author: Xiaoyu Guo

from RMC.model.input.base import YMLModelObject as BaseModel


class Materials(BaseModel):
    card_option_types = {
        # todo 补充相关选项的解析
    }

    def __init__(self, mats=None, unparsed=''):
        if mats is None:
            mats = []
        self._mats = mats
        self._unparsed = unparsed  # ceace, mgace, etc.

    @property
    def mats(self):
        return self._mats

    def add_mat(self, mat):
        if mat not in self._mats:
            self._mats.append(mat)

    def update_mat(self, mat_id, nuclides):
        for mat in self._mats:
            if mat.mat_id == mat_id:
                for nuclide in nuclides:
                    mat.update_nuclide(nuclide)

    def check(self):
        pass

    def __str__(self):
        card = 'MATERIAL\n'
        for mat in self._mats:
            card += str(mat) + '\n'
        if self._unparsed != '':
            card += self._unparsed
        card += '\n\n'
        return card


class Material(BaseModel):
    def __init__(self, mat_id=0, density=0, nuclides=None):
        self._mat_id = mat_id
        self._density = density

        if nuclides is None:
            nuclides = []
        self._nuclides = nuclides

    @property
    def mat_id(self):
        return self._mat_id

    @mat_id.setter
    def mat_id(self, mat_id):
        self._mat_id = mat_id

    @property
    def density(self):
        return self._density

    @density.setter
    def density(self, density):
        self._density = density

    def check(self):
        assert isinstance(self._mat_id, int)

    def update_nuclide(self, nuclide):
        for current_nuclide in self._nuclides:
            if current_nuclide.name == nuclide.name:
                current_nuclide.density = nuclide.density
                return

        self._nuclides.append(nuclide)

    def __str__(self):
        card = 'mat'
        card += ' ' + str(self._mat_id)
        card += ' ' + str(self._density)
        for nuclide in self._nuclides:
            card += ' ' + str(nuclide)
        return card


class Nuclide(BaseModel):
    def __init__(self, name=None, density=0):
        self._name = name
        self._density = density

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def density(self):
        return self._density

    @density.setter
    def density(self, density):
        self._density = density

    def check(self):
        pass

    def __str__(self):
        return self._name + ' ' + str(self._density)
