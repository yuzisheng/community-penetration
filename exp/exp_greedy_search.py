import igraph as ig
import multiprocessing as mp
from common import graph_load, graph_cal
from common.constant import INF_BUDGET
from baseline.greedy_search import GreedySearch


def exp_this_method(comm: ig.Graph, group: ig.Graph, budget: int, conv_rate: float):
    greedy_search = GreedySearch(budget, conv_rate)
    ops = greedy_search.run(comm.copy(), group.copy())
    print("budget {}, conv rate {}: {} {}".format(len(ops), conv_rate,
                                                  *graph_cal.cal_hidden_score(group.copy(), comm.copy(), ops)))


def diff_budget(comm: ig.Graph, group: ig.Graph, conv_rate: float):
    pool = mp.Pool(5)
    pool.starmap(exp_this_method, [(comm, group, _, conv_rate) for _ in range(1, 30)])


def diff_conv_rate(comm: ig.Graph, group: ig.Graph, budget: int):
    pool = mp.Pool(5)
    pool.starmap(exp_this_method, [(comm, group, budget, _) for _ in [0, 1, 5, 10, 20, 50]])


def diff_subs(comm: ig.Graph):
    subs = graph_cal.gen_groups_of_graph(comm)  # subs
    for sub in subs:
        sub_comm, sub_group = sub
        print("+++++++ comm:({}, {}) group:({}, {})".format(sub_comm.vcount(), sub_comm.ecount(),
                                                            sub_group.vcount(), sub_group.ecount()))
        if 0.1 * sub_comm.vcount() < sub_group.vcount() < 0.3 * sub_comm.vcount():
            diff_budget(sub_comm, sub_group, conv_rate=0)
            # diff_conv_rate(comm, sub_group, budget=10)


if __name__ == '__main__':
    lesmis = graph_load.load_graph_gml("../data/lesmis.gml", 'c-')
    k_graph = graph_load.create_full_graph(4, 'g-')  # complete graph
    # diff_budget(lesmis, k_graph, conv_rate=0)  # 1. diff budget
    # diff_conv_rate(lesmis, k_graph, budget=6)  # 2. diff conv rate
    # diff_subs(lesmis)
    print("ok")
