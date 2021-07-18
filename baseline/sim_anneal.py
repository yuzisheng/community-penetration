import math
import time
import random
import numpy as np
import igraph as ig
from itertools import product
from scipy.special import comb
from common import graph_cal, graph_load
from common.constant import BASE_WEIGHT


class SimulatedAnnealing:
    def __init__(self, budget: int, conv_rate: float):
        self.budget = budget
        self.conv_rate = conv_rate

    @staticmethod
    def is_valid_ops(ops: list, group: ig.Graph):
        ops_edges = [_[1] for _ in ops]
        add_ops = [_[1] for _ in ops if _[0] == 'add']
        del_ops = [_[1] for _ in ops if _[0] == 'del']
        # invalid 1: no 'add' ops
        if not len(add_ops):
            return False
        # invalid 2: duplicated add vertices in group or comm
        if len(set([_[0] for _ in add_ops])) != len([_[0] for _ in add_ops]) or len(
                set([_[1] for _ in add_ops])) != len([_[1] for _ in add_ops]):
            return False
        # invalid 3: duplicated ops
        if len(set(ops_edges)) != len(ops_edges):
            return False
        # invalid 4: unconnected
        group_copy = group.copy()  # in case group is modified
        for del_op in del_ops:
            group_copy.delete_edges([del_op])
        return True if group_copy.is_connected() else False

    def obj_fun(self, ops: list, group: ig.Graph, comm: ig.Graph) -> float:
        group_copy = group.copy()  # in case group is modified
        del_ops = [_[1] for _ in ops if _[0] == 'del']
        add_ops = [_[1] for _ in ops if _[0] == 'add']
        # cal after ops
        for del_op in del_ops:
            group_copy.delete_edges([del_op])
        out_score = 0
        for add_op in add_ops:
            g_v_name, c_v_name = add_op
            in_attraction = graph_cal.cal_as_of_vertex(group_copy, g_v_name)
            out_attraction = 1 + BASE_WEIGHT * comm.degree(c_v_name)
            out_score += (out_attraction / in_attraction)
        in_score = graph_cal.cal_safeness_of_graph(group_copy)
        convenience = graph_cal.cal_convenience_of_graph(group_copy)
        return -(out_score + in_score + self.conv_rate * convenience)  # min

    @staticmethod
    def judge(deltaE, T) -> bool:
        if deltaE < 0:
            return True
        else:
            prob = math.exp(-deltaE / T)
            return True if prob > np.random.rand() else False

    def disturbance(self, ops: list, group: ig.Graph, comm_top_vertices: list):
        op_choice = ['add', 'del']
        del_choice = [(group.vs[e.source]['name'], group.vs[e.target]['name']) for e in group.es]  # only existing edges
        add_choice = list(product(group.vs['name'], comm_top_vertices, repeat=1))  # [g_vs_name, c_vs_name]
        # mutate
        mutated_op_idx = random.choice([_ for _ in range(len(ops))])
        while True:
            mutated_name = random.choice(op_choice)
            mutated_edge = random.choice(del_choice) if mutated_name == 'del' else random.choice(add_choice)
            ops[mutated_op_idx] = (mutated_name, mutated_edge)
            if self.is_valid_ops(ops, group):
                break
        return ops

    def gen_valid_ops(self, group: ig.Graph, comm_top_vertices: list):
        op_choice = ['add', 'del']
        del_choice = [(group.vs[e.source]['name'], group.vs[e.target]['name']) for e in group.es]  # only existing edges
        add_choice = list(product(group.vs['name'], comm_top_vertices, repeat=1))  # [g_vs_name, c_vs_name]
        while True:
            ops = []
            for i in range(self.budget):
                op_name = random.choice(op_choice)
                op_edge = random.choice(del_choice) if op_name == 'del' else random.choice(add_choice)
                ops.append((op_name, op_edge))
            if self.is_valid_ops(ops, group):
                break
        return ops

    def run(self, group: ig.Graph, comm: ig.Graph):
        max_budget = group.vcount() + (group.ecount() - (group.vcount() - 1))  # max budget
        if self.budget > max_budget:
            self.budget = max_budget
        comm_top_vertices = [_[0] for _ in sorted([(_['name'], c.degree(_)) for _ in c.vs],
                                                  key=lambda x: x[1], reverse=True)[:self.budget]]
        curr_ops = self.gen_valid_ops(group, comm_top_vertices)
        curr_energy = self.obj_fun(curr_ops, group, comm)
        tot_cond = int(sum([comb(group.vcount(), i) * comb(group.vcount(), i) *
                            comb(group.ecount(), self.budget - i) for i in range(1, self.budget + 1)]))
        print("total condition: {}".format(tot_cond))
        alpha = 0.99
        tmp = 1e5
        tmp_min = 1e-2
        counter = 0
        counter_max = 50000
        while tmp >= tmp_min and counter <= counter_max:
            next_ops = self.disturbance(curr_ops, group, comm_top_vertices)
            next_energy = self.obj_fun(next_ops, group, comm)
            delta_energy = next_energy - curr_energy
            if self.judge(delta_energy, tmp):
                # accept
                curr_ops = next_ops
                curr_energy = next_energy
            if delta_energy < 0:
                tmp = tmp * alpha  # cool down
                # print("tmp: {}".format(tmp))
            else:
                counter += 1
        # print("best ops: {}, best score: {}".format(curr_ops, -curr_energy))
        # print("run over")
        return curr_ops


if __name__ == '__main__':
    c = graph_load.load_graph_gml("../data/karate.gml", 'c-')
    g = graph_load.create_multi_tree(2, 2, 'g-')
    start_time = time.time()
    sim_ann = SimulatedAnnealing(4, 0)
    ops = sim_ann.run(g.copy(), c.copy())
    end_time = time.time()
    print(ops)
    print("#hidden: {}, {} #time: {}s".format(*graph_cal.cal_hidden_score(
        g.copy(), c.copy(), ops), end_time - start_time))
    print("ok")
