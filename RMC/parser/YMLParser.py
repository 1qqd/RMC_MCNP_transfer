# -*- coding:utf-8 -*-
# author: Kaiwen Li
# date: 2019-11-15

import yaml
from yaml import Loader, Dumper

from RMC.model.input.Geometry import *
from RMC.model.input.refuelling import *


class YMLParser:
    def __init__(self, file_name):
        """
        Constructor of the YMLParser Class.
        :param file_name: the file to be parsed.
        """
        self.file = file_name
        self.data = {}
        self._parsed = False

    @property
    def parsed(self):
        """
        Parse the yaml input file, if parsed, directly return the data.
        :return: the data parsed from the input file.
        """
        if self._parsed:
            return self.data

        with open(self.file, 'r') as f:
            self.data = yaml.load(f, Loader)
        return self.data
