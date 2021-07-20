# -*- coding:utf-8 -*-
# author: Xiaoyu Guo

from RMC.model.input.base import YMLModelObject as BaseModel


class Mesh(BaseModel):
    def __init__(self, meshes=None):
        if meshes is None:
            meshes = []

        self._meshes = meshes

    @property
    def meshes(self):
        return self._meshes

    def add_one_mesh(self, mesh_info=None):
        if mesh_info is not None:
            self._meshes.append(mesh_info)

    def check(self):
        for mesh in self._meshes:
            mesh.check()

    def __str__(self):
        card = 'MESH\n'
        for mesh in self._meshes:
            card += str(mesh)
        card += '\n\n'
        return card


class MeshInfo(BaseModel):
    card_option_types = {
        'MESHINFO': [int],
        'TYPE': [int],
        'FILENAME': [str],
        'DATASETNAME': [str],
    }

    def __init__(self, mesh_info_id=None, mesh_type=None,
                 filename=None, datasetname=None):
        self._id = mesh_info_id
        self._type = mesh_type
        self._filename = filename
        self._datasetname = datasetname

    def check(self):
        assert self._id > 0
        assert self._type > 0

    def add_options(self, options):
        self._id = options['MESHINFO']
        self._type = options['TYPE']
        self._filename = options['FILENAME']
        self._datasetname = options['DATASETNAME']

    @property
    def id(self):
        return self._id

    @property
    def type(self):
        return self._type

    @property
    def filename(self):
        return self._filename

    @property
    def datasetname(self):
        return self._datasetname

    @id.setter
    def id(self, mesh_info_id):
        self._id = mesh_info_id

    @type.setter
    def type(self, mesh_type):
        self._type = mesh_type

    @filename.setter
    def filename(self, filename):
        self._filename = filename

    @datasetname.setter
    def datasetname(self, datasetname):
        self._datasetname = datasetname

    def __str__(self):
        card = 'MeshInfo '
        card += str(self._id) + ' '
        card += 'type = ' + str(self._type) + ' '
        card += 'filename = ' + str(self._filename) + ' '
        card += 'datasetname = ' + str(self._datasetname)
        card += '\n'
        return card
