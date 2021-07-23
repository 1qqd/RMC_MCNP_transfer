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

    def __init__(self, name=None, number=-1, bounds='', material=None, volume=None, fill=None, inner=False,
                 temperature=None, density=None, void=False, transformation=None, noburn=0, impn = None):
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
        self.impn = impn

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
            self.transformation = Transformation(
                move=options['MOVE'], rotate=options['ROTATE'])

    def count_cell(self, cell_id):
        if self.number == cell_id:
            return 1
        if self.fill is None:
            return 0
        elif self.include is None:
            raise ValueError(
                "Postprocessing for cell {} has not been done!".format(self.number))
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
        if self.impn is not None:
            s += 'imp:n=%f' % self.impn
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
        # only for lattice type 5
        'MAX': [int],
        'LENGTH': [float],
        'RADIUS': [float],
        'FILL_BALL': [int],
        'FILL_INTERVAL': [int],
        # for random geometry
        'MATRIC': [int],
        'PARTICLE': ['list', int, -1],
        'PF': ['list', float, -1],
        'RAD': ['list', float, -1],
        'RSA': [int],
        'TYPE': [int],
        'SIZE': ['list', float, -1],
        'DEM': [int],
        'TIME': [float],
        'PFCORRECT': [int]
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
            self.transformation = Transformation(
                move=options['MOVE'], rotate=options['ROTATE'])
        if options['LAT'] is not None:
            self.lattice = Lattice(type=options['LAT'], pitch=options['PITCH'], scope=options['SCOPE'],
                                   fill=options['FILL'], theta=options['SITA'], max_scope=options['MAX'],
                                   fill_ball=options['FILL_BALL'], fill_interval=options['FILL_INTERVAL'],
                                   radius=options['RADIUS'], length=options['LENGTH'], matric=options['MATRIC'],
                                   particle=options['PARTICLE'], pf=options['PF'], rad=options['RAD'],
                                   rsa=options['RSA'], typerg=options['TYPE'], sizerg=options['SIZE'], dem=options['DEM'],
                                   time=options['TIME'], pfcorrect=options['PFCORRECT'])

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
            raise ValueError(
                "Postprocessing for universe {} has not been done!".format(self.number))
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

    def __init__(self, pitch=np.zeros(3), scope=np.zeros(3), fill=None, type=None, theta=None,
                 length=None, radius=None, fill_ball=None, fill_interval=None, max_scope=None,  # lat=5
                 matric=None, particle=None, pf=None, rad=None, typerg=None, sizerg=None, pfcorrect=False, rsa=None,
                 dem=None, time=None  # lat=3 4
                 ):
        self.pitch = np.array(pitch)
        self.scope = np.array(scope)
        self.fill = np.array(fill)
        self.type = type
        self.theta = theta
        # lat = 3 4
        self.matric = matric
        self.particle = particle
        self.pf = pf
        self.rad = rad
        self.typerg = typerg
        self.sizerg = sizerg
        self.pfcorrect = pfcorrect
        self.rsa = rsa
        self.dem = dem
        self.time = time
        # lat = 5
        self.length = length
        self.radius = radius
        self.fill_ball = fill_ball
        self.fill_interval = fill_interval
        self.max_scope = max_scope

    def check(self):
        assert self.type >= 0

    def __str__(self):
        if self.type in [1, 2]:
            s = 'LAT=%d SCOPE=' % self.type
            for ele in self.scope:
                s += '%d ' % ele
            s += 'PITCH='
            for ele in self.pitch:
                s += '%f ' % ele
            if self.theta is not None and self.type == 2:
                s += 'SITA=%f ' % self.theta
            s += 'FILL='
            if len(set(self.fill)) == 1:
                s += '%d ' % self.fill[0]
                s += '* %d \n' % len(self.fill)
            else:
                for idx, val in enumerate(self.fill):
                    if idx % self.scope[0] == 0:
                        s += '\n '
                    s += '%d ' % val
            return s.replace(' \n', '\n').strip()
        elif self.type in [3, 4]:
            s = 'LAT=%d ' % self.type

            s += 'MATRIC=%d ' % self.matric
            s += 'PARTICLE='
            for ele in self.particle:
                s += '%d ' % ele
            s += 'PF='
            for ele in self.pf:
                s += '%f ' % ele
            s += 'RAD='
            for ele in self.rad:
                s += '%f ' % ele
            s += ' TYPE=%d ' % self.typerg
            s += 'SIZE='
            for ele in self.sizerg:
                s += '%f ' % ele
            if self.pfcorrect is not None:
                s += ' PFCORRECT=%d ' % self.pfcorrect
            if self.rsa is not None:
                s += ' RSA=%d ' % self.rsa
            if self.dem is not None:
                s += ' DEM=%d ' % self.dem
            if self.time is not None:
                s += ' TIME=%d ' % self.time
        elif self.type == 5:
            s = 'LAT=%d \n' % self.type
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
        assert self.move.shape == tuple(
            [3]) and self.rotate.shape == tuple([3, 3])

    def __str__(self):
        s = ''
        if self.move is not None:
            s += 'move='
            for idx, val in enumerate(self.move):
                s += '%f ' % val
        if self.rotate is not None:
            s += 'rotate='
            for idx, val in enumerate(self.rotate):
                s += '%.15f ' % val
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
            if univ.lattice is not None and univ.lattice.type in [1, 2]:
                for uid in univ.lattice.fill:
                    univ.include.add(self.univ_dict[uid])
            for cell in univ.cells:
                if cell.fill is not None:
                    cell.include = self.univ_dict[cell.fill]

    def get_univ(self, uid):
        return self.univ_dict[uid]

    def get_cell(self, cid):
        return self.cell_dict[cid]

    def proc_lat5(self):
        for univ in self.universes:
            if univ.lattice:
                if univ.lattice.type == 5:
                    post_scope = np.array([univ.lattice.max_scope, univ.lattice.max_scope, univ.lattice.max_scope])
                    post_pitch = np.array([univ.lattice.length, univ.lattice.length, univ.lattice.length])
                    post_fill = np.ones(univ.lattice.max_scope * univ.lattice.max_scope * univ.lattice.max_scope,
                                        dtype=int) * 18888
                    post_lat = Lattice(type=1, scope=post_scope, pitch=post_pitch, fill=post_fill)

                    post_univ = Universe(number=18888)  # 18888 is the default Universe index in Lat = 5
                    cell_num_list = [8888 + i for i in range(14)]  # 8888 to 8900 are the default Cell index in Lat = 5
                    l = univ.lattice.length
                    r = univ.lattice.radius
                    bounds = ''
                    for num in cell_num_list:
                        bounds = bounds + '&' + str(num)
                    cells = [
                        Cell(number=8999, bounds=bounds[1:len(bounds)], fill=univ.lattice.fill_interval, volume=None,
                             density=None),
                        Cell(number=cell_num_list[0], bounds=str(-cell_num_list[0]), fill=univ.lattice.fill_ball,
                             transformation=Transformation(move=[0, 0, 0]), volume=None, density=None),
                        Cell(number=cell_num_list[1], bounds=str(-cell_num_list[0]), fill=univ.lattice.fill_ball,
                             transformation=Transformation(move=[l, 0, 0]), volume=None, density=None),
                        Cell(number=cell_num_list[2], bounds=str(-cell_num_list[0]), fill=univ.lattice.fill_ball,
                             transformation=Transformation(move=[l, l, 0]), volume=None, density=None),
                        Cell(number=cell_num_list[3], bounds=str(-cell_num_list[0]), fill=univ.lattice.fill_ball,
                             transformation=Transformation(move=[0, l, 0]), volume=None, density=None),
                        Cell(number=cell_num_list[4], bounds=str(-cell_num_list[0]), fill=univ.lattice.fill_ball,
                             transformation=Transformation(move=[0, 0, l]), volume=None, density=None),
                        Cell(number=cell_num_list[5], bounds=str(-cell_num_list[0]), fill=univ.lattice.fill_ball,
                             transformation=Transformation(move=[l, 0, l]), volume=None, density=None),
                        Cell(number=cell_num_list[6], bounds=str(-cell_num_list[0]), fill=univ.lattice.fill_ball,
                             transformation=Transformation(move=[l, l, l]), volume=None, density=None),
                        Cell(number=cell_num_list[7], bounds=str(-cell_num_list[0]), fill=univ.lattice.fill_ball,
                             transformation=Transformation(move=[0, l, l]), volume=None, density=None),
                        Cell(number=cell_num_list[8], bounds=str(-cell_num_list[0]), fill=univ.lattice.fill_ball,
                             transformation=Transformation(move=[l / 2, 0, l / 2]), volume=None, density=None),
                        Cell(number=cell_num_list[9], bounds=str(-cell_num_list[0]), fill=univ.lattice.fill_ball,
                             transformation=Transformation(move=[l, l / 2, l / 2]), volume=None, density=None),
                        Cell(number=cell_num_list[10], bounds=str(-cell_num_list[0]), fill=univ.lattice.fill_ball,
                             transformation=Transformation(move=[l / 2, l, l / 2]), volume=None, density=None),
                        Cell(number=cell_num_list[11], bounds=str(-cell_num_list[0]), fill=univ.lattice.fill_ball,
                             transformation=Transformation(move=[0, l / 2, l / 2]), volume=None, density=None),
                        Cell(number=cell_num_list[12], bounds=str(-cell_num_list[0]), fill=univ.lattice.fill_ball,
                             transformation=Transformation(move=[l / 2, l / 2, l]), volume=None, density=None),
                        Cell(number=cell_num_list[13], bounds=str(-cell_num_list[0]), fill=univ.lattice.fill_ball,
                             transformation=Transformation(move=[l / 2, l / 2, 0]), volume=None, density=None)]
                    post_univ.add_cells(cells)
                    self.universes.append(post_univ)
                    # universe 添加完毕

                    # 8888 to 8900 are the default Surf index in Lat = 5
                    surfs = [Surface(number=cell_num_list[0], parameters=[0, 0, 0, r], stype='S'),
                             Surface(number=cell_num_list[1], parameters=[l, 0, 0, r], stype='S'),
                             Surface(number=cell_num_list[2], parameters=[l, l, 0, r], stype='S'),
                             Surface(number=cell_num_list[3], parameters=[0, l, 0, r], stype='S'),
                             Surface(number=cell_num_list[4], parameters=[0, 0, l, r], stype='S'),
                             Surface(number=cell_num_list[5], parameters=[l, 0, l, r], stype='S'),
                             Surface(number=cell_num_list[6], parameters=[l, l, l, r], stype='S'),
                             Surface(number=cell_num_list[7], parameters=[0, l, l, r], stype='S'),
                             Surface(number=cell_num_list[8], parameters=[l / 2, 0, l / 2, r], stype='S'),
                             Surface(number=cell_num_list[9], parameters=[l, l / 2, l / 2, r], stype='S'),
                             Surface(number=cell_num_list[10], parameters=[l / 2, l, l / 2, r], stype='S'),
                             Surface(number=cell_num_list[11], parameters=[0, l / 2, l / 2, r], stype='S'),
                             Surface(number=cell_num_list[12], parameters=[l / 2, l / 2, l, r], stype='S'),
                             Surface(number=cell_num_list[13], parameters=[l / 2, l / 2, 0, r], stype='S')]
                    # surfs 为返回值，添加完毕

                    univ.lattice = post_lat
                    # lat=5 解析完毕
                    return surfs

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
        if self.surfaces is None:
            self.surfaces = []

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
        s = 'SURFACE\n'
        for surf in self.surfaces:
            s += str(surf)
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

    def __init__(self, number=None, stype=None, parameters=None, boundary=None, pair=None):
        self._number = number
        self._type = stype
        self._parameters = parameters
        self._boundary = boundary
        self._pair = pair

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, number):
        self._number = number

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, stype):
        self._type = stype

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    def parameters(self, para):
        self._parameters = para

    @property
    def boundary(self):
        return self._boundary

    @boundary.setter
    def boundary(self, boundary):
        self._boundary = boundary

    @property
    def pair(self):
        return self._pair

    @pair.setter
    def boundary(self, pair):
        self._pair = pair

    def check(self):
        assert self._number >= 0

    def __str__(self):
        card = 'SURF ' + str(self._number) + ' ' + self._type + ' '
        surf_para = ' '.join([str(x) for x in self._parameters]) if isinstance(self._parameters, list) else ' ' + str(
            self._parameters)
        card += surf_para
        if self._boundary is not None:
            card += ' BC = ' + str(self._boundary)
        if self._pair is not None:
            card += ' PAIR = ' + str(self._pair)
        card += '\n'
        return card
