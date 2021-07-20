from unittest import TestCase
from RMC.controller.refuel import Refuel
from RMC.parser.PlainParser import PlainParser
import filecmp
import os
import shutil
import numpy as np


class TestRefuel(TestCase):
    def test_refuel(self):
        """

        :return:
        """
        # input files
        inp_initial = 'resources/inp_initial'
        refuel_inp = 'resources/refuelling.yml'
        inp = 'resources/inp'
        status_file = 'resources/status.txt'
        mat_ref = 'resources/mat_1_ref.npy'
        mat_bak = 'resources/mat_1_bak.npy'
        # material file will be changed in the test, so the mat_1.npy file is copied from mat_1_bak.npy
        #   in each time of testing.
        mat = 'resources/mat_1.npy'

        # output files
        output = 'resources/inp.refuel'

        # reference
        reference = 'resources/reference'

        shutil.copy(mat_bak, mat)

        # 0. Load the data and do a step of refuelling.
        refuel = Refuel(refuel_inp=refuel_inp)
        base_model = PlainParser(inp_initial).parsed
        refuel.refuel(1, inp, base_model, output=output)

        # 1. Check the plain input file
        self.assertTrue(filecmp.cmp(output, reference))

        # 2. Check the material npy file
        a = np.load(mat)
        b = np.load(mat_ref)
        try:
            self.assertTrue(np.all(a == b))
        except AssertionError:
            print("output: ")
            print(a)
            print("reference: ")
            print(b)
            exit(1)

        # 3. Postprocessing
        os.remove(output)
        os.remove(mat)

    # todo: add a test case with unused universe in the lattice.
