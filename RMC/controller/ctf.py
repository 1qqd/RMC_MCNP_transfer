# -*- coding:utf-8 -*-
# author: Xiaoyu GUO

import os


class FakeCTF:
    def __init__(self, inp):
        self.dir = os.path.dirname(inp)

    def run(self):
        assert os.path.exists(os.path.join(self.dir, 'deck.inp'))

        with open(os.path.join(self.dir, 'deck.ctf.h5'), 'w') as deck_h5:
            deck_h5.write('fake ctf h5 output')


class FakeCTFPreproc:
    def __init__(self, inp):
        self.dir = os.path.dirname(inp)

    def run(self):
        assert os.path.exists(os.path.join(self.dir, 'assem.inp'))
        assert os.path.exists(os.path.join(self.dir, 'geo.inp'))
        assert os.path.exists(os.path.join(self.dir, 'control.inp'))
        assert os.path.exists(os.path.join(self.dir, 'power.inp'))

        with open(os.path.join(self.dir, 'deck.inp'), 'w') as deckinp:
            deckinp.write('fake ctf input file')
