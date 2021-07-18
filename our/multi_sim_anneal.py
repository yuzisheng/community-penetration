import igraph as ig
from common import graph_cal, graph_load
from baseline.sim_anneal import SimulatedAnnealing


class MultiSimulatedAnnealing:
    def __init__(self, budget: int, conv_rate: float, multi: int):
        self.budget = budget
        self.conv_rate = conv_rate
        self.multi = multi

    def multi_run(self, group: ig.Graph, comm: ig.Graph):
        best_hidden_score = 0
        for i in range(self.multi):
            sim_ann = SimulatedAnnealing(self.budget, self.conv_rate)
            best_op = sim_ann.run(group, comm)
            _, hidden_score = graph_cal.cal_hidden_score(group, comm, best_op)
            if hidden_score > best_hidden_score:
                best_hidden_score = hidden_score
            print("iter {}:{}\n{} {}".format(i, best_op, _, hidden_score))


if __name__ == '__main__':
    facebook = graph_load.load_graph_txt("../data/facebook.txt", 'c-')
    attacker = graph_load.create_full_graph(6, 'g-')

    multi_sim_ann = MultiSimulatedAnnealing(4, 0, 1)
    multi_sim_ann.multi_run(attacker.copy(), facebook.copy())
    print("ok")
