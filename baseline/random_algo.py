import random
import igraph as ig
from itertools import product
from common import graph_cal, graph_load
from common.my_func import is_no_dup_elems
from common.constant import WEIGHT_DECREASE_LEVEL


class RandomAlgo:
    def __init__(self, pop_size: int):
        self.pop_size = pop_size

    @staticmethod
    def eliminate_invalid_dna(population: list, group: ig.Graph):
        # invalid 1: no 'add' operation
        first_valid_pop = []
        for dna in population:
            if 'add' in [_[0] for _ in dna]:
                first_valid_pop.append(dna)
        # invalid 2: duplicated add vertices in group or comm
        second_valid_pop = []
        for dna in first_valid_pop:
            add_genes = [_[1] for _ in dna if _[0] == 'add']
            add_group_vertices = [_[0] for _ in add_genes]
            add_comm_vertices = [_[1] for _ in add_genes]
            if is_no_dup_elems(add_group_vertices) and is_no_dup_elems(add_comm_vertices):
                second_valid_pop.append(dna)
        # invalid 3: del or add the same edges 2 times or more
        third_valid_pop = []
        for dna in second_valid_pop:
            if len(set([(gene[1][0], gene[1][1]) for gene in dna])) == len(dna):
                third_valid_pop.append(dna)
        # invalid 4: result in unconnected group
        fourth_valid_pop = []
        for dna in third_valid_pop:
            group_copy = group.copy()
            if_valid = True
            for gene in dna:
                if gene[0] == 'del':
                    group_copy.delete_edges([gene[1]])
                if not group_copy.is_connected():
                    if_valid = False
                    break
            if if_valid:
                fourth_valid_pop.append(dna)
        return fourth_valid_pop

    @staticmethod
    def score(ops: tuple, group: ig.Graph, comm: ig.Graph, conv_rate: float) -> float:
        group_copy = group.copy()  # in case group is modified
        del_ops = [_ for _ in ops if _[0] == 'del']
        add_ops = [_ for _ in ops if _[0] == 'add']
        # cal after ops
        for gene in del_ops:
            group_copy.delete_edges([gene[1]])
        out_score = 0
        for gene in add_ops:
            g_v_name, c_v_name = gene[1]
            in_attraction = graph_cal.cal_as_of_vertex(group_copy, g_v_name)
            out_attraction = 1 + WEIGHT_DECREASE_LEVEL * comm.degree(c_v_name)
            out_score += (out_attraction / in_attraction)
        in_score = graph_cal.cal_safeness_of_graph(group_copy)
        convenience = graph_cal.cal_convenience_of_graph(group_copy)
        return out_score + in_score + conv_rate * convenience

    def random_gen_valid_pop(self, group: ig.Graph, comm_top_vertices: list, budget: int):
        origin_pop = []
        ops = ['add', 'del']
        del_choice = [(group.vs[e.source]['name'], group.vs[e.target]['name']) for e in group.es]  # only existing edges
        add_choice = list(product(group.vs['name'], comm_top_vertices, repeat=1))  # [g_vs_name, c_vs_name]
        for i in range(self.pop_size):
            random_op = []
            for j in range(budget):
                op = random.choice(ops)
                edge = random.choice(del_choice) if op == 'del' else random.choice(add_choice)
                random_op.append((op, edge))
            origin_pop.append(tuple(random_op))  # list is not hashable
        origin_valid_pop = self.eliminate_invalid_dna(origin_pop, group)
        print("generate {}/{} origin valid population".format(len(origin_valid_pop), len(origin_pop)))
        return origin_valid_pop

    def run(self, group: ig.Graph, comm: ig.Graph, budget: int, conv_rate: float):
        max_budget = group.vcount() + (group.ecount() - (group.vcount() - 1))  # max budget
        if budget > max_budget:
            budget = max_budget
        comm_top_vertices = [_[0] for _ in sorted([(_['name'], comm.degree(_)) for _ in comm.vs],
                                                  key=lambda x: x[1], reverse=True)[:budget]]
        pop = self.random_gen_valid_pop(group, comm_top_vertices, budget)
        scores = [self.score(_, group, comm, conv_rate) for _ in pop]
        best_idx = scores.index(max(scores))
        # hidden_scores = [graph_cal.cal_hidden_score(group.copy(), comm.copy(), _)[1] for _ in pop]
        # print(scores)
        # print(hidden_scores)
        # plt.scatter(scores, hidden_scores)
        # plt.show()
        print("origin: best ops: {}, best score: {}".format(pop[best_idx], scores[best_idx]))


if __name__ == '__main__':
    c = graph_load.load_graph_gml("../data/lesmis.gml", 'c-')
    g = graph_load.create_full_graph(5, 'g-')
    random_algo = RandomAlgo(10000)
    random_algo.run(g, c, budget=6, conv_rate=0)
    print("ok")
