# -*- codint:utf-8 -*-

import os
import filecmp

import unittest
from unittest import TestCase
from RMC.controller.rmc import FakeRMC


class TestFakeRMC(TestCase):
    fake_rmc = None
    base_dir = None
    all_original_file = None

    @classmethod
    def setUp(cls):
        inp = 'resources/FakeRMC/inp'
        cls.fake_rmc = FakeRMC(inp)
        cls.base_dir = os.path.dirname(inp)
        cls.all_original_file = os.listdir(cls.base_dir)

    @classmethod
    def tearDown(cls):
        all_file = os.listdir(cls.base_dir)
        all_new_file = list(set(all_file) - set(cls.all_original_file))
        for file in all_new_file:
            os.remove(os.path.join(cls.base_dir, file))

    def test_new_name_start_with(self):
        self.assertEqual(
            self.fake_rmc.new_name_start_with('material'), 'material_2')

    def test_run(self):
        all_original_file = os.listdir(self.base_dir)
        self.fake_rmc.run()
        all_file = os.listdir(self.base_dir)
        all_new_file = list(set(all_file) - set(all_original_file))
        for file in all_new_file:
            self.assertTrue(
                filecmp.cmp(os.path.join(self.base_dir, file),
                            os.path.join(self.base_dir, 'reference', file)),
                'file {} is not matched!'.format(file))


if __name__ == '__main__':
    unittest.main()
