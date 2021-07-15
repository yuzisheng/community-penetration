import igraph as ig
import multiprocessing as mp
from common import graph_load, graph_cal
from common.constant import INF_BUDGET
from baseline.genetic_algo import GeneticAlgo


def exp_genetic_algo(comm: ig.Graph, group: ig.Graph, budget: int, conv_rate: float):
    genetic_algo = GeneticAlgo(pop_size=10000, sel_rate=0.9,
                               crossover_rate=0.8, mutate_rate=0.01, iter_times=100)
    ops = genetic_algo.run(group.copy(), comm.copy(), 10, 0)
    print("budget {}, conv rate {}: {} {}".format(budget, conv_rate,
                                                  *graph_cal.cal_hidden_score(group.copy(), comm.copy(), ops)))


def diff_budget(comm: ig.Graph, group: ig.Graph, conv_rate: float):
    pool = mp.Pool(5)
    pool.starmap(exp_genetic_algo, [(comm, group, _, conv_rate) for _ in range(1, 7)])


def diff_conv_rate(comm: ig.Graph, group: ig.Graph, budget: int):
    pool = mp.Pool(5)
    pool.starmap(exp_genetic_algo, [(comm, group, budget, _) for _ in [0, 1, 5, 10, 20, 50]])


if __name__ == '__main__':
    lesmis = graph_load.load_graph_gml("../data/lesmis.gml", 'c-')
    k_graph = graph_load.create_full_graph(5, 'g-')
    # diff_budget(lesmis, k_graph, conv_rate=0)  # 1. diff budget
    # diff_conv_rate(lesmis, k_graph, budget=6)  # 2. diff conv rate
    print("ok")
