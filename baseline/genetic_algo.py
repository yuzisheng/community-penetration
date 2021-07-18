import time
import random
import numpy as np
import igraph as ig
import matplotlib.pyplot as plt
from itertools import product
from common import graph_cal, graph_load
from common.my_func import is_no_dup_elems
from common.constant import BASE_WEIGHT


class GeneticAlgo:
    def __init__(self, pop_size: int, sel_rate: float, crossover_rate: float, mutate_rate: float,
                 iter_times: int):
        self.pop_size = pop_size
        self.dna_size = None  # need to be determined by budget
        self.sel_rate = sel_rate
        self.crossover_rate = crossover_rate
        self.mutate_rate = mutate_rate
        self.iter_times = iter_times

    def gen_origin_valid_pop(self, group: ig.Graph, comm_top_vertices: list):
        origin_pop = []
        ops = ['add', 'del']
        del_choice = [(group.vs[e.source]['name'], group.vs[e.target]['name']) for e in group.es]  # only existing edges
        add_choice = list(product(group.vs['name'], comm_top_vertices, repeat=1))  # [g_vs_name, c_vs_name]
        for i in range(self.pop_size):
            dna = []
            for j in range(self.dna_size):
                op = random.choice(ops)
                edge = random.choice(del_choice) if op == 'del' else random.choice(add_choice)
                dna.append((op, edge))
            origin_pop.append(tuple(dna))  # list is not hashable
        origin_pop = list(set(origin_pop))  # 去重
        origin_valid_pop = self.eliminate_invalid_dna(origin_pop, group)
        print("generate {}/{} origin valid population".format(len(origin_valid_pop), len(origin_pop)))
        return origin_valid_pop

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
    def fitness(dna: tuple, group: ig.Graph, comm: ig.Graph, conv_rate: float) -> float:
        group_copy = group.copy()  # in case group is modified
        del_genes = [_ for _ in dna if _[0] == 'del']
        add_genes = [_ for _ in dna if _[0] == 'add']
        # cal after ops
        for gene in del_genes:
            group_copy.delete_edges([gene[1]])
        out_score = 0
        for gene in add_genes:
            g_v_name, c_v_name = gene[1]
            out_attraction = 1 + BASE_WEIGHT * comm.degree(c_v_name)
            in_attraction = graph_cal.cal_as_of_vertex(group_copy, g_v_name)
            out_score += (out_attraction / in_attraction)
        in_score = graph_cal.cal_safeness_of_graph(group_copy)
        convenience = graph_cal.cal_convenience_of_graph(group_copy)
        return out_score + in_score + conv_rate * convenience

    def select(self, population: list, group: ig.Graph, comm: ig.Graph, conv_rate: float):
        fitness_scores = [self.fitness(_, group, comm, conv_rate) for _ in population]
        tot_score = sum(fitness_scores)
        survive_probs = list(map(lambda x: x / tot_score, fitness_scores))
        # select in valid pop by prob
        sel_dna_idxs = np.random.choice([i for i in range(len(population))],
                                        size=int(len(population) * self.sel_rate), replace=True, p=survive_probs)
        sel_pop = [population[_] for _ in sel_dna_idxs]
        return sel_pop

    def crossover(self, population: list):
        children_pop = []
        for dna in population:
            if np.random.rand() < self.crossover_rate:
                parent_dna_idx = random.choice([_ for _ in range(len(population))])
                cross_points = np.random.randint(0, 2, size=self.dna_size).astype(np.bool)
                child_dna = []
                for i in range(self.dna_size):
                    child_dna.append(population[parent_dna_idx][i] if cross_points[i] else dna[i])
                children_pop.append(child_dna)
        return children_pop

    def mutate(self, population: list, group: ig.Graph, comm_top_vertices: list):
        ops = ['add', 'del']
        del_choice = [(group.vs[e.source]['name'], group.vs[e.target]['name']) for e in group.es]  # only existing edges
        add_choice = list(product(group.vs['name'], comm_top_vertices, repeat=1))  # [g_vs_name, c_vs_name]
        mutated_pop = []
        for dna in population:
            for i in range(self.dna_size):
                if np.random.rand() < self.mutate_rate:
                    op_name = random.choice(ops)
                    op_edge = random.choice(del_choice) if op_name == 'del' else random.choice(add_choice)
                    dna[i] = (op_name, op_edge)
            mutated_pop.append(dna)
        return mutated_pop

    def evolution(self, population: list, group: ig.Graph, comm: ig.Graph, conv_rate: float, comm_top_vertices: list):
        sel_pop = self.select(population, group, comm, conv_rate)
        cross_pop = self.crossover(sel_pop)
        mutated_pop = self.mutate(cross_pop, group, comm_top_vertices)
        evolution_valid_pop = self.eliminate_invalid_dna(mutated_pop, group)
        return evolution_valid_pop

    def run(self, group: ig.Graph, comm: ig.Graph, budget: int, conv_rate: float):
        max_budget = group.vcount() + (group.ecount() - (group.vcount() - 1))  # max budget
        if budget > max_budget:
            budget = max_budget
        self.dna_size = budget
        comm_top_vertices = [_[0] for _ in sorted([(_['name'], comm.degree(_)) for _ in comm.vs],
                                                  key=lambda x: x[1], reverse=True)[:budget]]
        pop = self.gen_origin_valid_pop(group, comm_top_vertices)
        scores = [self.fitness(_, group, comm, conv_rate) for _ in pop]
        best_idx = scores.index(max(scores))
        # print("origin: best ops: {}, best score: {}".format(pop[best_idx], scores[best_idx]))
        avg_scores = []
        best_each_gen = [(pop[best_idx], scores[best_idx])]
        for i in range(self.iter_times):
            pop = self.evolution(pop, group, comm, conv_rate, comm_top_vertices)
            if len(pop) < 2:
                break
            scores = [self.fitness(_, group, comm, conv_rate) for _ in pop]
            best_idx = scores.index(max(scores))
            best_each_gen.append((pop[best_idx], scores[best_idx]))
            # print("iter {}: best ops: {}, best score: {}".format(i + 1, pop[best_idx], scores[best_idx]))
            avg_scores.append(sum([self.fitness(_, group, comm, conv_rate) for _ in pop]) / len(pop))
        # print("each iter avg score: {}".format(avg_scores))
        # for _ in best_each_gen: print(_)
        hidden_scores = [graph_cal.cal_hidden_score(group.copy(), comm.copy(), _[0])[1] for _ in best_each_gen]
        our_scores = [_[1] for _ in best_each_gen]
        # plt.scatter(our_scores, hidden_scores)
        # plt.show()
        return max(best_each_gen, key=lambda x: x[1])


if __name__ == '__main__':
    c = graph_load.load_graph_gml("../data/lesmis.gml", 'c-')
    g = graph_load.create_full_graph(5, 'g-')
    start_time = time.time()
    genetic_algo = GeneticAlgo(pop_size=20000, sel_rate=0.9,
                               crossover_rate=0.8, mutate_rate=0.01, iter_times=100)
    best = genetic_algo.run(g.copy(), c.copy(), budget=6, conv_rate=0)
    end_time = time.time()
    print("#hidden: {}, {} #time: {}s".format(*graph_cal.cal_hidden_score(
        g.copy(), c.copy(), best[0]), end_time - start_time))
    print("ok")
