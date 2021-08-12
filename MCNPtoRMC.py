# -*- coding:utf-8 -*-
# author: Shen PF
# date: 2021-07-23


import RMC.model.input.Material as RMCMat
import RMC.model.input.Geometry as RMCGeometry
import RMC.model.input.Criticality as RMCCriticality
from RMC.model.input.base import Model as RMCModel
import MCNP.parser.PlainParser as MCNPParser


def transfer(inp_MCNP):
    # inp_MCNP = '06'  # 'm0525' #

    M_model = MCNPParser.PlainParser(inp_MCNP).parsed
    with open(inp_MCNP + '_parsed_MCNP_model', 'w+') as f:
        f.write(str(M_model))

    R_model = RMCModel()

    # transfer surface block
    R_surfaces = []
    for M_surf in M_model.model['surface'].surfaces:
        surf = RMCGeometry.Surface(number=M_surf.number, stype=M_surf.type, parameters=M_surf.parameters,
                                   boundary=M_surf.boundary, pair=M_surf.pair)
        R_surfaces.append(surf)

    R_surfaces_model = RMCGeometry.Surfaces(surfaces=R_surfaces)
    test = str(R_surfaces_model)

    # transfer material block
    R_materials = []
    for cell in M_model.model['geometry'].cells:
        tmp_mat_id = cell.material
        if tmp_mat_id == 0:
            continue
        for index in range(len(M_model.model['materials'].mats)):
            if M_model.model['materials'].mats[index].mat_id == tmp_mat_id:
                M_model.model['materials'].mats[index].densities.append(cell.density)

    duplicate_mats = []
    for mat in M_model.model['materials'].mats:
        if mat.densities and len(set(mat.densities)) == 1:
            R_mat = RMCMat.Material(mat_id=mat.mat_id, density=mat.densities[0], nuclides=mat.nuclides)
            R_materials.append(R_mat)
        elif len(set(mat.densities)) > 1:
            duplicate_mats.append(mat.mat_id)
    if duplicate_mats:
        print('Warning: find duplicated mat densities, id:\n' + str(duplicate_mats) + '\nPlease pay attention!')

    R_sabs = ''
    for mt in M_model.model['materials'].mts:
        R_sabs += 'sab ' + str(mt.id) + ' ' + mt.name + '\n'

    R_materials_model = RMCMat.Materials(mats=R_materials, unparsed=R_sabs)
    test2 = str(R_materials_model)

    # transfer geometry block
    R_cells = []
    R_universes = []
    R_universes_ids = []
    for cell in M_model.model['geometry'].cells:
        out_universe_id = 0
        if cell.universe:
            out_universe_id = cell.universe
        R_cell = RMCGeometry.Cell(number=cell.number, bounds=cell.bounds.replace('#', '!'), material=cell.material,
                                  fill=cell.fill, impn=cell.impn)

        established_univ = False
        for index in range(len(R_universes_ids)):
            if R_universes_ids[index] == out_universe_id:
                R_universes[index].cells.append(R_cell)
                established_univ = True

        if not established_univ:
            R_lattice = None
            if cell.lat:
                R_lattice = RMCGeometry.Lattice(type=cell.lat)
                R_universe1 = RMCGeometry.Universe(number=out_universe_id, lattice=R_lattice)
                R_universe2 = RMCGeometry.Universe(number=out_universe_id * 100 + 1)
                R_universe2.cells.append(R_cell)
                R_universes.append(R_universe2)
                R_universes_ids.append(out_universe_id * 100 + 1)
                R_universes.append(R_universe1)
                R_universes_ids.append(out_universe_id)
            else:
                R_universe = RMCGeometry.Universe(number=out_universe_id, lattice=R_lattice)
                R_universe.cells.append(R_cell)
                R_universes.append(R_universe)
                R_universes_ids.append(out_universe_id)

    # 调整 universe 顺序
    R_universes = sorted(R_universes, key=lambda x: x.number)

    R_geometry_model = RMCGeometry.Geometry(universes=R_universes)
    test3 = str(R_geometry_model)

    # combine RMC model
    R_model.model['geometry'] = R_geometry_model
    R_model.model['surface'] = R_surfaces_model
    R_model.model['material'] = R_materials_model

    R_model.model['criticality'] = RMCCriticality.Criticality(
        unparsed='PowerIter population = 10000 50 300  keff0 = 1\nInitSrc point = 0 0 0')
    R_model.model['plot'] = 'PLOT\nPlotID 1 Type = slice Color = cell Pixels=10000 10000 Vertexes=-100 -100 0 100 100 0\nPlotID 2 type = slice color = cell pixels=10000 10000 vertexes=-100 0 -100 100 0 100'

    # output 2 files
    with open(inp_MCNP + '_parsed_RMC_model', 'w+') as f:
        f.write(str(R_model))

    print('file: [' + inp_MCNP + '] have been processed!\n')
