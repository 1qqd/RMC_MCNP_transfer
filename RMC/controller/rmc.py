# -*- coding:utf-8 -*-
# author: Kaiwen Li
# date: 2019-11-27

from RMC.controller.controller import Controller
from RMC.parser.PlainParser import PlainParser
from RMC.controller.refuel import Refuel
from RMC.parser.YMLParser import YMLParser

from RMC.model.input.Include import IncludeMaterial

import os
import shutil
import glob


class RMCController(Controller):
    class Options:
        def __init__(self, burnup=False, refuel=False,
                     couple=False, pcqs=False):
            self.burnup = burnup
            self.refuel = refuel
            self.couple = couple
            self.pcqs = pcqs

    def __init__(self, inp, archive):
        self.inp = inp
        self.model = PlainParser(inp).parsed
        self.update_inp()

        self.iteration = 1
        self.archive = archive

        self.last_archive = self.archive
        self.last_inp = self.inp

        # define calculation options
        burnup_mode = False
        refuel_mode = False
        couple_mode = False
        pcqs_mode = False

        if self.model['burnup'] is not None:
            burnup_mode = True

        if self.model['refuelling'] is not None:
            refuel_mode = True
            self.refuel = Refuel(os.path.join(os.path.dirname(self.inp),
                                              self.model['refuelling'].file))
        else:
            self.refuel = None

        if self.model['criticality'] is not None:
            if self.model['criticality'].couple_option:
                couple_mode = True

        self.options = RMCController.Options(burnup=burnup_mode,
                                             refuel=refuel_mode,
                                             couple=couple_mode,
                                             pcqs=pcqs_mode)

        # todo 增加接续计算功能

    def check(self, status_file):
        """
        Check whether the execution finished by inspecting the status file.
        :param status_file: The path to the status file printed by RMC.
        :return:
        """
        status = YMLParser(status_file).parsed['RMC']
        step = 0
        for cycle_entry in status[:-1]:
            cycle = cycle_entry['cycle']
            step += len(cycle) - 1

        last_cycle = status[-1]['cycle']
        if 'output' in last_cycle[-1]:
            step += len(last_cycle) - 1
            inp = last_cycle[-1]['output']
        else:
            raise NotImplementedError('Burnup restart feature currently '
                                      'not supported in Python Package.')

        if self.refuel is not None:
            output_file = self.refuel.refuel(step, inp, self.model)
            if output_file is not None:
                return [False, output_file]
            else:
                return [True]
        return [True]

    def new_inp_archive(self):
        new_inp = self.inp
        new_archive = self.archive

        if self.options.burnup:
            new_inp += '.burnup.' + str(self.model['burnup'].current_step)
            new_archive = os.path.join(
                new_archive, 'burnup' + str(self.model['burnup'].current_step))

        if self.options.couple:
            new_inp += '.couple.' + str(self.iteration)
            new_archive = os.path.join(
                new_archive, 'couple' + str(self.iteration))

        return [new_inp, new_archive]

    def continuing(self, status_file, propt):

        if self.options.couple:
            if self.iteration == 1:
                if not self.options.burnup or \
                        self.model['burnup'].current_step == 0:
                    # 在耦合计算刚刚开始时，为热工程序生成初始的正弦功率分布
                    # RMC要求用于耦合计算的网格计数器在计数器选项卡中的编号必须是1
                    print('Generating sine shaped power distribution for CTF'
                          'as first guess of the results\n', flush=True)
                    # 在第一次计算之前，先清理先前的计算可能残留的文件
                    meshtally = os.path.join(os.path.dirname(propt['inp']),
                                             'MeshTally*')
                    trash_files = glob.glob(meshtally)
                    for trash in trash_files:
                        os.remove(trash)
                    # 生成功率
                    self.generate_tally_hdf(self.model['tally'].meshtally[0],
                                            os.path.dirname(propt['inp']))

        propt['inp'], propt['archive_dir'] = self.new_inp_archive()

        if not self.options.burnup:
            if not self.options.couple:
                # 无燃耗、无耦合的RMC计算，只需要算一次，不需要改输入卡
                if self.iteration == 1:
                    self.iteration += 1
                    return True
                else:
                    return False
            else:
                # 无燃耗，有耦合的RMC计算，需要迭代到耦合结束
                if self.iteration <= self.model['criticality'].max_iteration:
                    with open(propt['inp'], 'w') as f:
                        f.write(str(self.model))
                    self.iteration += 1
                    return True
                else:
                    return False
        else:
            # 燃耗步都执行完成后，就结束计算
            if self.model['burnup'].current_step > \
                    self.model['burnup'].step_number:
                return False

            # 解析输入卡
            if self.model['burnup'].current_step == 0:
                # 解析初始输入卡
                cur_model = PlainParser(self.inp).parsed
                if os.path.exists(propt['inp'] + '.State.h5'):
                    os.remove(propt['inp'] + '.State.h5')
            else:
                # 解析上个燃耗步生成的接续输入卡
                last_fmt_inp = os.path.join(
                    self.last_archive,
                    os.path.basename(self.last_inp) + '.FMTinp.step1'
                )
                cur_model = PlainParser(last_fmt_inp).parsed

            # 复制接续文件
            if self.model['burnup'].current_step > 0:
                # 当不是初始燃耗步时，把上个燃耗步生成的material文件copy过来
                shutil.copy(
                    os.path.join(self.last_archive,
                                 cur_model['includematerial'].material),
                    os.path.dirname(self.inp)
                )
                if self.model['burnup'].current_step < \
                        self.model['burnup'].step_number:
                    # 当不是最后一个燃耗步时（最后一个燃耗步不做点燃耗计算），
                    # 把上个燃耗步生成的包含点燃耗核素信息的文件copy过来
                    last_state = os.path.join(
                        self.last_archive,
                        os.path.basename(self.last_inp) + '.State.h5'
                    )
                    shutil.copy(last_state, propt['inp'] + '.State.h5')

            # 处理耦合迭代
            if self.options.couple:
                if self.iteration <= self.model['criticality'].max_iteration:
                    # 临界耦合迭代中
                    # 累加迭代计数器
                    self.iteration += 1
                    # 不进行临界搜索和点燃耗计算
                    cur_model['criticalitysearch'] = None
                    cur_model['burnup'] = None
                    cur_model['refuelling'] = None
                    cur_model['print'] = None
                else:
                    # 迭代结束后，进行燃耗计算（可能伴有临界搜索等）
                    # 重置迭代计数器
                    self.iteration = 1

            # iteration = 1 表示这一步将做点燃耗计算。
            # 在无耦合时，iteration就等于1；在有耦合时，在耦合最后一步也置为1
            if self.iteration == 1:
                # 推进燃耗步
                self.model['burnup'].current_step += 1
                # 记录当前燃耗步所用的输入卡和存储位置信息，下个燃耗步会用得到
                self.last_archive = propt['archive_dir']
                self.last_inp = propt['inp']

            # 生成实际计算所需要的输入卡
            with open(propt['inp'], 'w') as f:
                f.write(str(cur_model))

            return True

        # if status_file is None:
        #     warnings.warn('Status file not specified, continuous running can not be performed.')
        #     return False
        # status = self.check(status_file)
        # if status[0]:
        #     return False
        # else:
        #     # todo: more elegant method to modify the parameters.
        #     property['inp'] = status[1]
        #     property['conti'] = True
        #     return True

    @staticmethod
    def generate_tally_hdf(meshtally, h5file_dir):
        """基于解析RMC输入卡得到的网格计数器模型，
        生成一个轴向余弦分布的网格计数器结果HDF5文件，提供给第一次CTF计算使用。

        :param meshtally: 解析RMC输入卡的到的网格计数器模型
        :param h5file_dir: HDF5文件的生成目录
        """
        import numpy as np
        from RMC.controller.RMCEnum import TallyType, MeshType

        def fine_bounds(coarse_bounds, bin_number):
            """ 基于粗网（网格边界坐标和细网格数）计算细网

            :param coarse_bounds: 粗网边界，例如[0.0, 1.0, 3.0]表示粗网有三个边界，
                分别是1.0, 2.0, 3.0
            :param bin_number: 细网格数目，例如[4, 8]表示第一个粗网格中有两个细网格，
                第二个粗网格中有8个细网格
            :return: 细网
            """
            _fine_bounds = []
            for coarse_index in range(len(coarse_bounds) - 1):
                bin_size = coarse_bounds[coarse_index + 1] - \
                           coarse_bounds[coarse_index]  # 细网格的尺寸
                for i in range(bin_number[coarse_index]):
                    # 依次添加细网边界坐标
                    _fine_bounds.append(
                        coarse_bounds[coarse_index] +
                        bin_size / bin_number[coarse_index] * i)
            # 补充上最后的边界坐标
            _fine_bounds.append(coarse_bounds[-1])
            return _fine_bounds

        def sine_power(bounds_x, bounds_y, bounds_z):
            """根据各个方向上的边界（细网），计算所有网格的尺寸（体积）。

            :param bounds_x: x方向上的细网边界，由小到大排列
            :param bounds_y: y方向上的细网边界，由小到大排列
            :param bounds_z: z方向上的细网边界，由小到大排列
            """
            x_bin_num = len(bounds_x) - 1  # mesh bin number in x direction
            y_bin_num = len(bounds_y) - 1  # mesh bin number in y direction
            z_bin_num = len(bounds_z) - 1  # mesh bin number in z direction

            z_bin_center = np.ones(z_bin_num)  # mesh bin center in z direction
            for z_idx in range(z_bin_num):
                z_bin_center[z_idx] = \
                    (bounds_z[z_idx] + bounds_z[z_idx + 1]) / 2.0
            z_length = bounds_z[-1] - bounds_z[0]  # length in z direction

            from math import sin, pi
            # volume of all the meshes
            power = np.ones((x_bin_num, y_bin_num, z_bin_num))
            for x_idx in range(x_bin_num):
                for y_idx in range(y_bin_num):
                    for z_idx in range(z_bin_num):
                        # 功率 = 体积 × 功率密度
                        # 功率密度为正弦分布（堆底为0点）
                        power[x_idx, y_idx, z_idx] = \
                            (bounds_x[x_idx + 1] - bounds_x[x_idx]) * \
                            (bounds_y[y_idx + 1] - bounds_y[y_idx]) * \
                            (bounds_z[z_idx + 1] - bounds_z[z_idx]) * \
                            sin((z_bin_center[z_idx] - bounds_z[0]) / z_length
                                * pi)

            return power

        if meshtally.scope is not None:
            # 均匀结构化网格
            x = meshtally.scope[0]
            y = meshtally.scope[1]
            z = meshtally.scope[2]
            fine_bound_x = fine_bounds([meshtally.bound[0],
                                        meshtally.bound[1]], [x])
            fine_bound_y = fine_bounds([meshtally.bound[2],
                                        meshtally.bound[3]], [y])
            fine_bound_z = fine_bounds([meshtally.bound[4],
                                        meshtally.bound[5]], [z])
        else:
            # 非均匀结构化网格
            x = np.sum(np.array(meshtally.scopex))
            y = np.sum(np.array(meshtally.scopey))
            z = np.sum(np.array(meshtally.scopez))
            fine_bound_x = fine_bounds(meshtally.boundx, meshtally.scopex)
            fine_bound_y = fine_bounds(meshtally.boundy, meshtally.scopey)
            fine_bound_z = fine_bounds(meshtally.boundz, meshtally.scopez)

        bound = []
        bound.extend(fine_bound_x)
        bound.extend(fine_bound_y)
        bound.extend(fine_bound_z)

        power = sine_power(fine_bound_x, fine_bound_y, fine_bound_z)

        import h5py

        # 当前版本的耦合计算要求固定使用下列参数：
        # 用于耦合的网格计数器的编号为1
        mesh_tally_id = 1
        # 用于耦合的网格类型为非均匀的结构化网格
        mesh_type = int(MeshType.nonuniform_structured_mesh)
        # 用于耦合的统计量为功率
        tally_type = int(TallyType.type_power)

        # RMC的网格计数器输出的HDF5文件名为MeshTally{id}.h5
        filename = os.path.join(h5file_dir,
                                u'MeshTally{}.h5'.format(mesh_tally_id))
        h5file = h5py.File(filename, 'w')

        geometry = h5file.create_group('Geometry')
        geometry.attrs['MeshType'] = mesh_type
        geometry.create_dataset('BinNumber', data=np.array([x, y, z]))
        geometry.create_dataset('Boundary', data=np.array(bound))

        h5file.create_dataset('Type' + str(tally_type), data=power)
        h5file.close()

        shutil.copyfile(filename, filename + '.previous')

    def update_inp(self):
        # 去掉@符号
        # todo 最好是在run_fileprocess中就处理了
        shutil.copy(self.inp, self.inp + '.bak')
        with open(self.inp, 'w+') as f:
            f.write(str(self.model))


class FakeRMC:
    """假RMC，可以基于RMC的输入卡，生成部分假结果。
    用于辅助对python流程控制代码进行快速debug。
    """

    def __init__(self, inp):
        """初始化

        :param inp: RMC的输入卡文件名
        """
        self.inp = inp

    def new_name_start_with(self, base):
        """生成以指定字符串开头的文件名，新文件名以数字结尾区分。

        :param base: 文件名的固定开头
        :return: 新文件名
        """
        if not os.path.exists(os.path.join(os.path.dirname(self.inp), base)):
            return base
        new_name = base
        index = 1
        while os.path.exists(os.path.join(os.path.dirname(self.inp),
                                          new_name)):
            new_name = base + '_' + str(index)
            index += 1
        return new_name

    def run(self):
        """通过解析RMC的输入卡，生成各种输出文件。
        输出的文件中绝大多数都是垃圾内容。
        """
        # dependencies
        assert os.path.exists(os.path.join(os.path.dirname(self.inp), 'xsdir'))

        original_model = PlainParser(self.inp).parsed

        # fake normal results
        with open(self.inp + '.out', 'w') as inpout:
            inpout.write('fake rmc out')
        with open(self.inp + '.Tally', 'w') as tally:
            tally.write('fake rmc tally')
        with open(self.inp + '.material', 'w') as material:
            material.write('fake rmc material')
        with open(self.inp + '.Adjoint', 'w') as adjoint:
            adjoint.write('fake rmc adjoint')

        # fake formatted inp for PRINT block
        if original_model['print'] is not None:
            if original_model['print'].inpfile == 1:
                mat_name = self.new_name_start_with('material')
                with open(os.path.join(os.path.dirname(self.inp),
                                       mat_name), 'w') as material:
                    material.write(str(original_model['material']))
                original_model['material'] = None
                original_model['includematerial'] = IncludeMaterial(mat_name)
                with open(self.inp + '.FMTinp.step0', 'w') as fmtinp:
                    fmtinp.write(str(original_model))

        # fake burnup results
        if original_model['burnup'] is not None:
            assert os.path.exists(os.path.join(os.path.dirname(self.inp),
                                               'DepthMainLib'))

            with open(self.inp + '.burn.den_tot', 'w') as dentot:
                dentot.write('fake rmc dentot')
            with open(self.inp + '.burn.power', 'w') as burnpower:
                burnpower.write('fake rmc power')
            with open(self.inp + '.depth.error', 'w') as error:
                error.write('fake rmc error')

        # fake formatted inp after burnup
        if original_model['burnup'] is not None:
            if original_model['print'] is not None:
                if original_model['print'].inpfile == 1:
                    # 以下的参数都是无意义的
                    original_model['burnup'].succession = {
                        'SINGLESTEP': 1,
                        'POWER': 123456789.123456789,
                        'TIMESTEP': 50,
                        'POINTBURNUP': 1,
                    }

                    mat_name = self.new_name_start_with('material')
                    with open(os.path.join(os.path.dirname(self.inp),
                                           mat_name), 'w') as material:
                        material.write(str(original_model['material']))

                    with open(self.inp + '.State.h5', 'w') as nuclide:
                        nuclide.write('fake rmc state')

                    original_model['material'] = None
                    original_model['includematerial'] = \
                        IncludeMaterial(mat_name)
                    with open(self.inp + '.FMTinp.step1', 'w') as fmtinp:
                        fmtinp.write(str(original_model))

        print("Fake simulation finished.")


if __name__ == '__main__':
    controller = RMCController(inp='inp', archive='archive')
