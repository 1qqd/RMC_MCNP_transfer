# -*- coding:utf-8 -*-
# author: Xiaoyu GUO

import os
import shutil
import h5py
import numpy as np

from RMC.controller.RMCEnum import TallyType


def power_ave(file_name, ave_scheme=8):
    """进行功率平均

    :param file_name: RMC输出的HDF5格式的功率文件的文件名
    :param ave_scheme: 4或者8。4：以1/4堆芯进行平均；8：以1/8堆芯进行平均
    """
    assert ave_scheme == 4 or ave_scheme == 8

    # 当前版本的耦合计算要求固定使用下列参数：
    # 用于耦合的统计量为功率
    tally_type = int(TallyType.type_power)

    dataset_name = 'Type{}'.format(tally_type)

    h5file = h5py.File(file_name, 'r+')
    """
    1  1  1  1  1  1  1  1  1  1  1
    1  1  x5 1  1  1  1  1  x6 1  1
    1  x1 1  1  1  1  1  1  1  x2 1
    1  1  1  1  1  1  1  1  1  1  1
    1  1  1  1  1  1  1  1  1  1  1
    1  1  1  1  1  1  1  1  1  1  1
    1  1  1  1  1  1  1  1  1  1  1
    1  1  1  1  1  1  1  1  1  1  1
    1  1  1  1  1  1  1  1  1  1  1
    1  x3 1  1  1  1  1  1  1  x4 1
    1  1  x7 1  1  1  1  1  x8 1  1
    1  1  1  1  1  1  1  1  1  1  1

    x1: origin
    x2: flip_x
    x3: flip_y
    x4: flip_xy

    x5: transpose
    x6: flip_x_transpose
    x7: flip_y_transpose
    x8: flip_xy_transpose
    """
    origin = h5file[dataset_name][()]
    origin = origin / np.sum(origin)
    flip_x = np.flip(origin, 0)
    flip_y = np.flip(origin, 1)
    flip_xy = np.flip(flip_x, 1)

    ave = origin + flip_x + flip_y + flip_xy

    if ave_scheme == 8:
        ave += np.transpose(origin, (1, 0, 2))   # transpose
        ave += np.transpose(flip_x, (1, 0, 2))   # flip_x_transpose
        ave += np.transpose(flip_y, (1, 0, 2))   # flip_y_transpose
        ave += np.transpose(flip_xy, (1, 0, 2))  # flip_xy_transpose

    ave /= ave_scheme

    previous_file = file_name + '.previous'
    if os.path.exists(previous_file):
        h5file_previous = h5py.File(previous_file, 'r')
        previous = h5file_previous[dataset_name][()]
        previous = previous / np.sum(previous)
        h5file_previous.close()
        ave = (ave + previous) / 2.0

    del h5file[dataset_name]
    h5file[dataset_name] = ave
    h5file.close()

    # 存档
    shutil.copyfile(file_name, previous_file)
