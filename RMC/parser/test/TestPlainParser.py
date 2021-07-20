from unittest import TestCase

from RMC.parser.PlainParser import PlainParser
import filecmp
import os


class TestPlainParser(TestCase):
    def test_parsed(self):
        test_case = 'resources/inp'
        parser = PlainParser(test_case)
        model = parser.parsed
        print_file = 'resources/parsed_and_print'
        reference_file = 'resources/reference'
        with open(print_file, 'w') as f:
            f.write(str(model))
        self.assertTrue(filecmp.cmp(print_file, reference_file))
        os.remove(print_file)

    def test_count_cell(self):
        test_case = 'resources/inp'
        parser = PlainParser(test_case)
        model = parser.parsed
        self.assertEqual(model['geometry'].univ_dict[0].count_cell(3), 3)
        self.assertEqual(model['geometry'].univ_dict[0].count_cell(8), 1)
        self.assertEqual(model['geometry'].univ_dict[1].count_cell(3), 1)
        self.assertEqual(model['geometry'].cell_dict[1].count_cell(3), 3)
        self.assertEqual(model['geometry'].cell_dict[1].count_cell(2), 0)
        self.assertEqual(model['geometry'].cell_dict[2].count_cell(5), 0)
