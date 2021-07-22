# -*- coding:utf-8 -*-
# author: Shen PF
# date: 2021-07-20

import yaml
import abc


# todo: change all of the classes inherited from this class, from __init__ to __new__, and
#       construct a __dict__ checking process.
class YMLModelObject(yaml.YAMLObject):
    """
    The method utilized by YAML package to construct Python object:
    1. use cls.__new__(cls) to create a new object
    2. use __setstate__ to update the parameter list
       or use __dict__.update() to directly update the parameter list
    3. yield the object.
    Note that, that process will not call the __init__ method, and some unexpected parameters
    can be introduced into the parameter dict, therefore, a checking method is required.
    """
    # todo: check method should be called after construction, and the __dict__ should be checked
    #       to avoid unexpected parameters from wrong input files.
    @abc.abstractmethod
    def check(self):
        pass

    @abc.abstractmethod
    def __str__(self):
        pass

    def postprocess(self):
        pass


class Model(YMLModelObject):
    def __init__(self, model=None):
        if model is None:
            model = {
                'geometry': None,
                'surface': None,
                'materials': None,
                'unparsed': None
            }
        self.model = model

    def check(self):
        for key in self.model.keys():
            if key is not 'unparsed' and self.model[key] is not None:
                self.model[key].check()

    def postprocess(self):
        self.check()
        if self.model['geometry'] is not None:
            self.model['geometry'].postprocess()

    def __str__(self):
        s = ''
        for key in self.model.keys():
            if key is not 'unparsed' and self.model[key] is not None:
                s += str(self.model[key])
        for card in self.model['unparsed']:
            s += card + '\n\n'
        return s

    def __getitem__(self, item):
        if item in self.model:
            return self.model[item]
        else:
            return None

    def __setitem__(self, item, value):
        if item in self.model:
            self.model[item] = value
        else:
            raise AttributeError('Model ' + item + 'is not supported.')
