# -*- codint:utf-8 -*-

import os
import h5py
import numpy as np

import unittest
from unittest import TestCase
from RMC.util.CoupleUtils import power_ave
from RMC.controller.RMCEnum import TallyType


class TestCoupleUtils(TestCase):
    def test_power_ave(self):
        # 当前版本的耦合计算要求固定使用下列参数：
        # 用于耦合的统计量为功率
        tally_type = int(TallyType.type_power)

        file_name = 'test_power_ave.h5'
        dataset_name = 'Type{}'.format(tally_type)

        # 先生成一个假的文件
        h5file = h5py.File(file_name, 'w')
        data = np.arange(1., 17., 1.).reshape([4, 4, 1])
        data[data > 10] = 20
        h5file[dataset_name] = data
        h5file.close()

        # 对假文件做一次1/4平均
        power_ave(file_name, 4)
        reference_ave_4 = np.array(
            [[45 / 4, 45 / 4, 45 / 4, 45 / 4],
             [42 / 4, 43 / 4, 43 / 4, 42 / 4],
             [42 / 4, 43 / 4, 43 / 4, 42 / 4],
             [45 / 4, 45 / 4, 45 / 4, 45 / 4]]
        ).reshape([4, 4, 1])
        # 对比1/4平均的结果
        ave_4 = h5py.File(file_name, 'r')[dataset_name][()]
        self.assertTrue(np.array_equal(reference_ave_4, ave_4))

        # 再做一次1/8平均
        power_ave(file_name, 8)
        reference_ave_8 = np.array(
            [[45 / 4, 87 / 8, 87 / 8, 45 / 4],
             [87 / 8, 43 / 4, 43 / 4, 87 / 8],
             [87 / 8, 43 / 4, 43 / 4, 87 / 8],
             [45 / 4, 87 / 8, 87 / 8, 45 / 4]]
        ).reshape([4, 4, 1])
        # 对比1/8平均的结果
        ave_8 = h5py.File(file_name, 'r')[dataset_name][()]
        self.assertTrue(np.array_equal(reference_ave_8, ave_8))

        os.remove(file_name)
        os.remove(file_name + '.bak')


if __name__ == '__main__':
    unittest.main()
