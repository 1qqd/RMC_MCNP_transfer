# -*- coding:utf-8 -*-
# author: Shen PF
# date: 2021-07-20

from RMC.model.input.base import YMLModelObject as BaseModel


class Materials(BaseModel):
    card_option_types = {
        # todo 补充相关选项的解析
    }

    def __init__(self, mats=None, mts=None, unparsed=''):
        if mats is None:
            mats = []
        self.mats = mats
        if mts is None:
            mts = []
        self.mts = mts
        self._unparsed = unparsed  # ceace, mgace, etc.

    def add_mat(self, mat):
        if mat not in self.mats:
            self.mats.append(mat)

    def add_mt(self, mt):
        if mt not in self.mts:
            self.mts.append(mt)

    def check(self):
        pass

    def __str__(self):
        card = ''
        for mat in self.mats:
            card += str(mat) + '\n'
        for mt in self.mts:
            card += str(mt) + '\n'
        if self._unparsed != '':
            card += 'Warning: No parsed card in Material block: \n' + self._unparsed
        card += '\n\n'
        return card


class Material(BaseModel):
    def __init__(self, mat_id=0, nuclides=None):
        self.mat_id = mat_id
        self.densities = []

        if nuclides is None:
            nuclides = []
        self.nuclides = nuclides

    def check(self):
        assert isinstance(self.mat_id, int)

    def update_nuclide(self, nuclide):
        for current_nuclide in self.nuclides:
            if current_nuclide.name == nuclide.name:
                current_nuclide.density = nuclide.density
                return

        self.nuclides.append(nuclide)

    def __str__(self):
        card = 'm'
        card += str(self.mat_id) + '\n'
        for nuclide in self.nuclides:
            card += ' ' + str(nuclide) + '\n'
        return card


class Nuclide(BaseModel):
    def __init__(self, name=None, density=0):
        self.name = name
        self.density = density

    def check(self):
        pass

    def __str__(self):
        return self.name + ' ' + str(self.density)


class Mt(BaseModel):
    def __init__(self, name, id):
        self.name = name
        self.id = id

    def check(self):
        pass

    def __str__(self):
        return 'mt' + str(self.id) + ' ' + self.name
