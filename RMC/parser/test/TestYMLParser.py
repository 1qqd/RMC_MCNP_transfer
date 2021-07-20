import os
import unittest
import yaml

from RMC.parser.YMLParser import YMLParser


# todo: More check should be done to confirm the test.
class TestYMLParser(unittest.TestCase):
    def test_refuelling(self):
        input_file = 'resources/refuelling.yml'
        parser = YMLParser(input_file)
        data = parser.parsed
        output_file = input_file + '.output.yml'
        f = open(output_file, 'w')
        yaml.dump(data, stream=f, default_flow_style=False)
        f.close()
        parser_re_read = YMLParser(output_file)
        re_read_data = parser_re_read.parsed
        self.assertEqual(data, re_read_data)
        os.remove(output_file)

    def test_geometry(self):
        parser = YMLParser('resources/geometry.yml')
        data = parser.parsed
        self.assertNotEqual(data, None)

