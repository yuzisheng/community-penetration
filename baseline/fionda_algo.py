import random
import igraph as ig
from common import graph_load


class FlondaAlgo:
    def __init__(self, budget):
        self.budget = budget

    @staticmethod
    def v_score(g_after_del: ig.Graph, v_name: str, ops_series: list):
        v_num = g_after_del.vcount()
        g_add_vs = [_[1][0] for _ in ops_series if _[0] == 'add']  # add_op: ('add', (g_v_name, c_v_name))
        v_in_degree = g_after_del.degree(v_name)
        v_out_degree = g_add_vs.count(v_name)
        v_score = (len(g_after_del.subcomponent(v_name)) - v_in_degree) / (v_num - 1) + v_out_degree / (
                v_out_degree + v_in_degree)
        return v_score

    def g_score(self, g_after_del: ig.Graph, ops_series: list):
        g_score = 0
        for v_name in g_after_del.vs['name']:
            g_score += self.v_score(g_after_del, v_name, ops_series)
        return g_score / g_after_del.vcount()

    def best_add(self, group: ig.Graph, comm: ig.Graph, ops_series: list, curr_score: float):
        # find v_p
        v_p = min([(_, self.v_score(group, _, ops_series)) for _ in group.vs['name']], key=lambda x: x[1])[0]
        # find v_t
        c_add_vs = [_[1][1] for _ in ops_series if _[0] == 'add' and _[1][0] == v_p]
        while True:
            v_t = random.choice([_ for _ in comm.vs['name']])
            if v_t not in c_add_vs:
                break
        # cal add gain
        ops_series.append(('add', (v_p, v_t)))
        next_score = self.g_score(group, ops_series)
        ops_series.pop()  # pop this op
        return ('add', (v_p, v_t)), next_score - curr_score

    def best_del(self, group: ig.Graph, ops_series: list, curr_score: float):
        del_scores = []
        for e in group.es:
            v1, v2 = group.vs[e.source]['name'], group.vs[e.target]['name']
            group.delete_edges([(v1, v2)])
            if group.is_connected():
                next_del_score = self.g_score(group, ops_series)
                del_scores.append((('del', (v1, v2)), next_del_score - curr_score))
            group.add_edge(v1, v2)  # add (v1, v2)) back
        return max(del_scores, key=lambda x: x[1]) if len(del_scores) else (('no_del', (None, None)), -1)

    def run(self, group: ig.Graph, comm: ig.Graph):
        max_budget = group.vcount() + (group.ecount() - (group.vcount() - 1))  # max budget
        if self.budget > max_budget:
            self.budget = max_budget
        ops_series = []
        curr_score = self.g_score(group, ops_series)
        print("curr score: {}".format(curr_score))
        while True:
            add_op, add_gain = self.best_add(group, comm, ops_series, curr_score)
            del_op, del_gain = self.best_del(group, ops_series, curr_score)
            if add_gain >= del_gain and add_gain > 0:
                # do add
                ops_series.append(add_op)
                curr_score = self.g_score(group, ops_series)  # change curr score
            elif del_gain > 0:
                # do del
                ops_series.append(del_op)
                group.delete_edges([del_op[1]])  # group del edge
                curr_score = self.g_score(group, ops_series)  # change curr score
            self.budget -= 1
            print("curr score: {}".format(curr_score))
            if self.budget < 0 or (add_gain < 0 and del_gain < 0):
                break
        print(ops_series)
        print("run done")


if __name__ == '__main__':
    c = graph_load.load_graph_gml("../data/lesmis.gml", 'c-')
    g = graph_load.create_full_graph(5, 'g-')
    flonda_algo = FlondaAlgo(budget=10)
    flonda_algo.run(g, c)
    print("ok")
