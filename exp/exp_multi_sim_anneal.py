import igraph as ig
import multiprocessing as mp
from common import graph_load, graph_cal
from our.multi_sim_anneal import MultiSimulatedAnnealing


def exp_this_method(group: ig.Graph, comm: ig.Graph, budget: int, conv_rate: float, multi: int):
    multi_sim_ann = MultiSimulatedAnnealing(budget, conv_rate, multi)
    ops = multi_sim_ann.multi_run(group.copy(), comm.copy())
    print("budget {}, conv rate {}: {} {}".format(len(ops), conv_rate,
                                                  *graph_cal.cal_hidden_score(group.copy(), comm.copy(), ops)))


def diff_budget(group: ig.Graph, comm: ig.Graph, conv_rate: float, multi: int):
    for budget in range(1, 10):
        exp_this_method(group, comm, budget, conv_rate, multi)


def diff_conv_rate(group: ig.Graph, comm: ig.Graph, budget: int, multi: int):
    pool = mp.Pool(5)
    pool.starmap(exp_this_method, [(group, comm, budget, _, multi) for _ in [0, 1, 5, 10, 20, 50]])


def diff_subs(comm: ig.Graph, multi: int):
    subs = graph_cal.gen_groups_of_graph(comm)  # subs
    for sub in subs:
        print("++++++++")
        sub_comm, sub_group = sub
        # diff_budget(sub_group, sub_comm, 0, 3)
        exp_this_method(sub_group, sub_comm, budget=4, conv_rate=0, multi=multi)
        # print("+++++++ comm:(v{}, e{}) group:(v{}, e{})".format(sub_comm.vcount(), sub_comm.ecount(),
        #                                                         sub_group.vcount(), sub_group.ecount()))
        # if 0.1 * sub_comm.vcount() < sub_group.vcount() < 0.3 * sub_comm.vcount():
        #     diff_budget(sub_group, sub_comm, conv_rate=0)


if __name__ == '__main__':
    karate = graph_load.load_graph_gml("../data/karate.gml", 'c-')

    # k_graph = graph_load.create_full_graph(4, 'g-') # complete graph
    # diff_budget(lesmis, k_graph, conv_rate=0)  # 1. diff budget
    # diff_conv_rate(lesmis, k_graph, budget=6)  # 2. diff conv rate

    diff_subs(karate, 1)

    print("ok")
