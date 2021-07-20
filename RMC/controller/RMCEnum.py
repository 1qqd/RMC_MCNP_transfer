# -*- coding:utf-8 -*-

from enum import IntEnum


class MeshType(IntEnum):
    """RMC的Mesh类所定义的网格类型。见 CoupleMesh::BaseMesh::MeshType 枚举型"""
    uniform_structured_mesh = 1
    nonuniform_structured_mesh = 2
    triangle_mesh = 3
    tetrahedral_mesh = 4


class TallyType(IntEnum):
    """RMC的网格计数器所统计的参数类型。见RMC用户手册中对网格计数器输入卡的Type的定义"""
    type_flux = 1
    type_power = 2
    type_fission_rate = 3
    type_absorption_rate = 4
    type_fission_neutron_rate = 5
