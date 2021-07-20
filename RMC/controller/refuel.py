# -*- coding:utf-8 -*-
# author: Kaiwen Li
# date: 2019-11-16

from RMC.parser.YMLParser import YMLParser
from RMC.parser.PlainParser import PlainParser

import os
import re
import numpy as np
import warnings


class Refuel:
    def __init__(self, refuel_inp):
        self.base_dir = ""
        self.refuel_inp = refuel_inp
        self.plan = {}
        self._get_refuel_model()

    def _get_refuel_model(self):
        refuel_model = YMLParser(self.refuel_inp).parsed['refuelling']
        for refuel in refuel_model.lists:
            self.plan[refuel.step] = refuel.plan

    def refuel(self, step, inp, base_model, output=None):
        # this step is not a refuelling step.
        if step not in self.plan:
            return None
        else:
            for refuel_step in self.plan:
                if refuel_step < step:
                    del(self.plan[refuel_step])

        if not os.path.isfile(inp):
            raise FileExistsError("File {} does not exists.".format(inp))
        self.base_dir = os.path.dirname(inp)

        plan = self.plan[step]
        cur_model = PlainParser(inp).parsed
        for univ_plan in plan:
            univ_id = univ_plan.universe
            univ = cur_model.geometry.get_univ(univ_id)
            mat_list = self._get_related_mat_file_list(univ=univ)
            exchange_strategy = Refuel._extract_strategy(alias=univ_plan.alias, mapping=univ_plan.mapping)
            Refuel._do_refuel(univ_plan.position, univ, mat_list, exchange_strategy, cur_model, base_model)
        if output is not None:
            output_file = output
        else:
            output_file = inp + '.refuel_%d.inp' % step
        with open(output_file, 'w') as f:
            f.write(str(cur_model))

        del(self.plan[step])
        return output_file

    @staticmethod
    def _extract_strategy(alias, mapping):
        pattern = re.compile(r'([A-Za-z_]+)(\d+)')
        n_row = len(mapping)
        n_column = len(mapping[0])
        for i in range(n_row):
            for j in range(n_column):
                if mapping[i][j] == 0:
                    mapping[i][j] = None
                else:
                    m = pattern.match(mapping[i][j])
                    if m:
                        if m.group(1) == alias['new']:
                            mapping[i][j] = int(m.group(2))
                        else:
                            mapping[i][j] = [alias['row'].index(int(m.group(2))),
                                             alias['column'].index(m.group(1))]
                    else:
                        raise ValueError('Entry %s in refuelling can not be recognized!' % mapping[i][j])

        strategy = {}
        for i in range(n_row):
            for j in range(n_column):
                initial = i * n_column + j
                if mapping[i][j] is not None:
                    if isinstance(mapping[i][j], list):
                        current = mapping[i][j][0] * n_column + mapping[i][j][1]
                        strategy[initial] = current
                    else:  # new assembly
                        strategy[initial] = -mapping[i][j]
                else:
                    strategy[initial] = initial

        return strategy

    def _get_related_mat_file_list(self, univ):
        mat_list = {}
        univ_stack = [univ]
        while len(univ_stack) > 0:
            universe = univ_stack.pop()
            if len(universe.include) > 0:
                univ_stack.extend(universe.include)
            else:
                for cell in universe:
                    if cell.fill is not None:
                        univ_stack.append(cell.include)
                    elif cell.material < 0:
                        mat_list[cell.number] = -cell.material

        return {cell: os.path.join(self.base_dir, 'mat_{}.npy'.format(mat_list[cell])) for cell in mat_list}

    @staticmethod
    def _do_refuel(pos, univ, mat_list, strategy, cur_model, base_model):
        initial = univ.lattice.fill.copy()
        new_assemblies = {}
        for idx in strategy:
            if strategy[idx] >= 0:
                univ.lattice.fill[idx] = initial[strategy[idx]]
            else:
                univ.lattice.fill[idx] = -strategy[idx]
                new_assemblies[idx] = -strategy[idx]
        """
        The expanding method in RMC is DFS, thus those cells belonging to the refuelling universe will be
        neighbors, so only the starting and ending index is needed.
        Also, DFS defines the sorting metric.
        """
        for cell_id in mat_list:
            mat_file = mat_list[cell_id]
            mat = np.load(mat_file)
            shape = mat.shape
            """
            0. Find the indexes that will be treated, start and end.
            1. Change the index to move assembly.
            2. Delete some indexes of assemblies that are moved out.
            3. Add material entries for new assemblies.
            4. Sort the cells to fulfill the requirement of RMC lattice material input.
            """
            pos = np.array(pos)
            rev_strategy = Refuel._reverse_strategy(strategy)

            start = -1
            end = -1
            pattern = None
            idx = 0
            while idx <= len(mat):
                if idx == len(mat):
                    if start >= 0:
                        end = idx
                    else:
                        break
                else:
                    cell_mat = mat[idx, :]
                    [is_match, pattern] = Refuel._check_pattern_match([pattern, pos], cell_mat, univ,
                                                                      model=cur_model)
                    if start < 0:
                        if is_match:
                            start = idx
                        idx += 1
                        continue
                    else:
                        if is_match:
                            idx += 1
                            continue
                        else:
                            end = idx
                            pattern = None

                aim_cells = mat[start:end, :].copy()
                mat = np.delete(mat, range(start, end), axis=0)
                univ_depth = len(pos) + 1  # the idx in the mat_row of the No. inside the lattice.
                to_be_deleted = []

                for aim_idx in range(len(aim_cells)):
                    cell = aim_cells[aim_idx]
                    if cell[univ_depth] - 1 in rev_strategy:
                        cell[univ_depth] = rev_strategy[cell[univ_depth] - 1] + 1
                    else:
                        to_be_deleted.append(aim_idx)

                modified_cells = list(np.delete(aim_cells, to_be_deleted, axis=0))

                # Add material entries for new assemblies.
                # todo: refactor needed.
                for assem_pos in new_assemblies:
                    univ_id = new_assemblies[assem_pos]
                    new_univ = cur_model.geometry.get_univ(univ_id)
                    initial_mat = base_model.geometry.get_cell(cell_id).material
                    count = new_univ.count_cell(cell_id)
                    if count > 0:
                        mats = np.zeros((count, shape[1]), dtype=int)
                        mats[:, 0] = -initial_mat
                        mats[:, univ_depth] = assem_pos + 1
                        modified_cells.extend(list(mats))

                sorted_cells = sorted(modified_cells, key=lambda array: (array[univ_depth]))
                if end - start != len(sorted_cells):
                    warnings.warn("Number of cells removed and inserted does not match!")
                    idx = start + len(sorted_cells)

                mat = np.insert(mat, start, np.array(sorted_cells), axis=0)
                start = -1
            np.save(mat_file, mat)

    @staticmethod
    def _reverse_strategy(strategy):
        rev_strategy = {}
        for key in strategy:
            if strategy[key] >= 0:
                if strategy[key] in rev_strategy:
                    raise ValueError('Refuelling matrix error, duplicate assemblies.')
                rev_strategy[strategy[key]] = key
        return rev_strategy

    @staticmethod
    def _check_pattern_match(pattern, cell_vec, univ, model):
        length = len(pattern[1])
        if pattern[0] is not None:
            is_match = np.all(pattern[0] == cell_vec[1:length + 1])
            return [is_match, pattern[0]]
        else:
            is_match = True
            for i in range(length):
                if pattern[1][i] > 0 and pattern[1][i] != cell_vec[i + 1]:
                    is_match = False
                    break
            if is_match:
                cell = model.geometry.get_cell(cell_vec[length])
                if cell.include == univ:
                    return [True, np.array(cell_vec[1:length + 1])]
                else:
                    return [False, None]
            else:
                return [False, None]
