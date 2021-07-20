# -*- coding:utf-8 -*-
# author: Kaiwen Li
# date: 2019-11-15

from RMC.model.input.base import YMLModelObject as BaseModel
import numpy as np


class Cell(BaseModel):
    yaml_tag = u'!cell'
    card_option_types = {
        'FILL': [int],
        'CELL': [int],
        'MAT': [str],
        'VOL': [float],
        'TMP': [float],
        'DENS': [float],
        'VOID': [bool],
        'INNER': [bool],
        'MOVE': ['list', float, 3],
        'ROTATE': ['list', float, 9],
        'NOBURN': [bool],
    }

    def __init__(self, name=None, number=-1, bounds='', material=None, volume=0, fill=None, inner=False,
                 temperature=None, density=0.0, void=False, transformation=None, noburn=0):
        self.name = name
        self.number = number
        self.bounds = bounds
        self.fill = fill
        self.inner = inner
        self.material = material
        self.temperature = temperature
        self.volume = volume
        self.density = density
        self.void = void
        self.transformation = transformation
        self.include = None  # included universe
        self.noburn = noburn

    def check(self):
        # assert self.temperature > 0
        assert self.number >= 0

    def add_bounds(self, bounds):
        self.bounds = bounds
        pass

    def add_options(self, options):
        self.fill = options['FILL']
        self.material = options['MAT']
        self.volume = options['VOL']
        self.temperature = options['TMP']
        self.density = options['DENS']
        self.void = options['VOID']
        self.inner = options['INNER']
        self.noburn = options['NOBURN']
        if options['MOVE'] is not None or options['ROTATE'] is not None:
            self.transformation = Transformation(move=options['MOVE'], rotate=options['ROTATE'])

    def count_cell(self, cell_id):
        if self.number == cell_id:
            return 1
        if self.fill is None:
            return 0
        elif self.include is None:
            raise ValueError("Postprocessing for cell {} has not been done!".format(self.number))
        else:
            return self.include.count_cell(cell_id)

    def __str__(self):
        s = 'CELL %d %s ' % (self.number, self.bounds)
        if self.material is not None:
            s += 'mat=%s ' % self.material
        if self.fill is not None:
            s += 'fill=%d ' % self.fill
        if self.inner:
            s += 'inner=1 '
        if self.temperature is not None:
            s += 'tmp=%f ' % self.temperature
        if self.volume is not None:
            s += 'vol=%f ' % self.volume
        if self.density is not None:
            s += 'dens=%f ' % self.density
        if self.void:
            s += 'void=1 '
        if self.noburn:
            s += 'noburn=1'
        if self.transformation is not None:
            s += str(self.transformation) + ' '
        return s.strip() + '\n'


class Universe(BaseModel):
    yaml_tag = u'!universe'
    card_option_types = {
        'FILL': ['list', int, -1],
        'SCOPE': ['list', int, 3],
        'PITCH': ['list', float, 3],
        'LAT': [int],
        'MOVE': ['list', float, 3],
        'ROTATE': ['list', float, 9],
        'SITA': [float],
        # todo: random geometry temporarily not supported.
    }

    def __init__(self, name=None, number=-1, cells=None, transformation=None, lattice=None):
        if cells is None:
            cells = []
        self.name = name
        self.number = number
        self.cells = cells
        self.transformation = transformation
        self.lattice = lattice
        self.include = set()

    def check(self):
        assert self.number >= 0

    def add_options(self, options):
        if options['MOVE'] is not None or options['ROTATE'] is not None:
            self.transformation = Transformation(move=options['MOVE'], rotate=options['ROTATE'])
        if options['LAT'] is not None:
            self.lattice = Lattice(type=options['LAT'], pitch=options['PITCH'], scope=options['SCOPE'],
                                   fill=options['FILL'], theta=options['SITA'])

    def add_cells(self, cells):
        self.cells.extend(cells)

    def postprocess(self):
        # todo: decorate the postprocess method with checking.
        self.check()
        for cell in self.cells:
            cell.postprocess()
        if self.lattice is not None:
            self.lattice.postprocess()
        if self.transformation is not None:
            self.transformation.postprocess()

    def count_cell(self, cell_id):
        num = 0
        if self.lattice is None:
            for cell in self.cells:
                num += cell.count_cell(cell_id)
        elif self.include is None:
            raise ValueError("Postprocessing for universe {} has not been done!".format(self.number))
        else:
            # todo: refactor needed.
            unique, counts = np.unique(self.lattice.fill, return_counts=True)
            occurrence = dict(zip(unique, counts))
            for univ in self.include:
                if univ.number in occurrence:
                    num += occurrence[univ.number] * univ.count_cell(cell_id)
        return num

    def __str__(self):
        s = 'UNIVERSE %d ' % self.number
        if self.transformation is not None:
            s += str(self.transformation) + ' '
        if self.lattice is not None:
            s += str(self.lattice)
        s += '\n'
        for cell in self.cells:
            s += str(cell)
        s += '\n'
        return s

    def __iter__(self):
        for cell in self.cells:
            yield cell


class Lattice(BaseModel):
    yaml_tag = u'!lattice'

    def __init__(self, pitch=np.zeros(3), scope=np.zeros(3), fill=None, type=None, theta=None):
        self.pitch = np.array(pitch)
        self.scope = np.array(scope)
        self.fill = np.array(fill)
        self.type = type
        self.theta = theta

    def check(self):
        assert self.type >= 0

    def __str__(self):
        s = 'LAT=%d SCOPE=' % self.type
        for ele in self.scope:
            s += '%d ' % ele
        s += 'PITCH='
        for ele in self.pitch:
            s += '%f ' % ele
        if self.theta is not None and self.type == 2:
            s += 'SITA=%f ' % self.theta
        s += 'FILL='
        for idx, val in enumerate(self.fill):
            if idx % self.scope[0] == 0:
                s += '\n '
            s += '%d ' % val
        return s.replace(' \n', '\n').strip()


class Transformation(BaseModel):
    yaml_tag = u'!transformation'

    def __init__(self, move=None, rotate=None):
        if move is not None:
            self.move = np.array(move)
        else:
            self.move = None
        if rotate is not None:
            self.rotate = np.array(rotate)
        else:
            self.rotate = None

    def check(self):
        assert self.move.shape == tuple([3]) and self.rotate.shape == tuple([3, 3])

    def __str__(self):
        s = ''
        if self.move is not None:
            s += 'move='
            for idx, val in enumerate(self.move):
                s += '%f ' % val
        if self.rotate is not None:
            s += 'rotate='
            for idx, val in enumerate(self.rotate):
                s += '%f ' % val
        return s.strip()


class Geometry(BaseModel):
    yaml_tag = u'!geometry'

    def __init__(self, universes=None):
        if universes is None:
            universes = []
        self.universes = universes
        self.univ_dict = {}
        self.cell_dict = {}

    def check(self):
        assert len(self.universes) > 0

    def add_universe(self, univ):
        self.universes.append(univ)

    def postprocess(self):
        for univ in self.universes:
            self.univ_dict[univ.number] = univ
            for cell in univ.cells:
                self.cell_dict[cell.number] = cell
        for univ in self.universes:
            univ.postprocess()
            if univ.lattice is not None:
                for uid in univ.lattice.fill:
                    univ.include.add(self.univ_dict[uid])
            for cell in univ.cells:
                if cell.fill is not None:
                    cell.include = self.univ_dict[cell.fill]

    def get_univ(self, uid):
        return self.univ_dict[uid]

    def get_cell(self, cid):
        return self.cell_dict[cid]

    def __str__(self):
        s = ''
        for univ in self.universes:
            s += str(univ)
        return s

    def __iter__(self):
        for univ in self.universes:
            yield univ


class Surfaces(BaseModel):
    yaml_tag = u'!surfaces'

    def __init__(self, surfaces=None):
        self.surfaces = surfaces

    def check(self):
        pass

    def __str__(self):
        s = 'SURFACE\n'
        for surf in self.surfaces:
            s += str(surf)


class Surface(BaseModel):
    yaml_tag = u'!surface'

    def __init__(self, number, type, parameters):
        self.number = number
        self.type = type
        self.parameters = parameters

    def check(self):
        assert self.number >= 0

    # todo:
    def __str__(self):
        return ''
