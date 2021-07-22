# -*- coding:utf-8 -*-
# author: Shen PF
# date: 2021-07-23


import RMC.model.input.Material as RMCMat
import RMC.model.input.Geometry as RMCGeometry
from RMC.model.input.base import Model as RMCModel
import MCNP.model.Geometry as MCNPGeometry
import MCNP.model.Material as MCNPMat
import MCNP.parser.PlainParser as MCNPParser

print("hello! Begin with the MCNP to RMC transformation tools.\n")

inp_MCNP = 'm0525'  # '06'  # 'm0525' #

M_model = MCNPParser.PlainParser(inp_MCNP).parsed

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


pass
