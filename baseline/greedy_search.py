import igraph as ig
from common import graph_cal, graph_load
from common.constant import INF_BUDGET, WEIGHT_DECREASE_LEVEL


def sub_modular(score: list) -> bool:
    inc_score = [score[i + 1] - score[i] for i in range(len(score) - 1)]
    return all(x >= y for x, y in zip(inc_score, inc_score[1:]))


class GreedySearch:
    def __init__(self, budget: int, conv_rate: float):
        self.budget = budget
        self.conv_rate = conv_rate
        self.vs_name_of_out_es = []  # [(c_v_name, g_v_name)]
        self.ops = []  # [(op_name, (c_v_name/g_v_name, g_v_name))]
        self.score = []

    def cal_score(self, comm: ig.Graph, group: ig.Graph) -> float:
        out_safe = 0
        for i in range(len(self.vs_name_of_out_es)):
            c_v_name, g_v_name = self.vs_name_of_out_es[i]
            out_attraction = 1 + WEIGHT_DECREASE_LEVEL * comm.degree(c_v_name)
            in_attraction = graph_cal.cal_as_of_vertex(group, g_v_name)
            out_safe += (out_attraction / in_attraction - 1)
        in_safe = graph_cal.cal_safeness_of_graph(group)
        score = out_safe + in_safe + self.conv_rate * graph_cal.cal_convenience_of_graph(group)
        return score

    def first_add_out_edge(self, comm: ig.Graph, group: ig.Graph):
        new_comm = graph_load.union_two_graphs(comm, group)  # init new community
        c_degree = {_['name']: comm.degree(_) for _ in comm.vs}
        c_v_with_max_degree = max(c_degree, key=c_degree.get)  # find the vertex of max degree in community
        # greedy strategy: choose the vertex with max degree as the vertex with highest attract score
        g_attract_score = {_['name']: graph_cal.cal_as_of_vertex(group, _['name']) for _ in group.vs}
        g_v_with_min_attract_score = min(g_attract_score, key=g_attract_score.get)
        new_comm.add_edge(c_v_with_max_degree, g_v_with_min_attract_score)  # add an out edge
        self.ops.append(('add', (c_v_with_max_degree, g_v_with_min_attract_score)))  # update op
        self.vs_name_of_out_es.append((c_v_with_max_degree, g_v_with_min_attract_score))
        self.score.append(self.cal_score(comm, group))
        return new_comm

    def select_op(self, comm: ig.Graph, group: ig.Graph):
        """ select operation: 1. delete inside edge; 2. add outside edge """
        pre_score = self.cal_score(comm, group)
        # 1. delete inside edges
        delete_inside_edge = {}
        for e in group.es:
            v1, v2 = group.vs[e.source]['name'], group.vs[e.target]['name']
            group.delete_edges([(v1, v2)])
            if group.is_connected():
                score_after_del = self.cal_score(comm, group)
                if score_after_del > pre_score:
                    delete_inside_edge[(v1, v2)] = score_after_del - pre_score
            group.add_edge(v1, v2)  # add edge back (not execute op here)
        if len(delete_inside_edge):
            del_op = max(delete_inside_edge, key=delete_inside_edge.get)
            del_op_gain = delete_inside_edge[del_op]
        else:
            del_op, del_op_gain = None, None
        # 2. add outside edges: link C(max degree) and G(min attract score)
        c_degree = {_['name']: comm.degree(_) for _ in comm.vs
                    if _['name'] not in [_[0] for _ in self.vs_name_of_out_es]}
        g_attract_score = {_['name']: graph_cal.cal_as_of_vertex(group, _['name']) for _ in group.vs
                           if _['name'] not in [_[1] for _ in self.vs_name_of_out_es]}
        add_op, add_op_gain = None, None
        if len(g_attract_score) and len(c_degree):
            # (c_vertex, g_vertex)
            add_c_v = max(c_degree, key=c_degree.get)
            add_g_v = min(g_attract_score, key=g_attract_score.get)
            self.vs_name_of_out_es.append((add_c_v, add_g_v))
            score_after_add = self.cal_score(comm, group)
            self.vs_name_of_out_es.pop()  # del edge back
            if score_after_add >= pre_score:
                add_op = (max(c_degree, key=c_degree.get), min(g_attract_score, key=g_attract_score.get))
                add_op_gain = score_after_add - pre_score
        # 3. select operation
        if (del_op and (not add_op) and del_op_gain > 0) or (
                del_op and add_op and del_op_gain > add_op_gain and del_op_gain > 0):
            return 'del', del_op
        elif (add_op and (not del_op) and add_op_gain > 0) or (
                del_op and add_op and add_op_gain > del_op_gain and add_op_gain > 0):
            return 'add', add_op
        else:
            return 'end', ('none', 'none')

    def execute_op(self, group: ig.Graph, new_community: ig.Graph, op_name: str,
                   op_vs: tuple) -> (bool, ig.Graph, ig.Graph):
        """ execute operation """
        if_continue = True
        if op_name == 'del':
            self.ops.append(('del', op_vs))  # update op
            group.delete_edges([op_vs])
            new_community.delete_edges([op_vs])
        elif op_name == 'add':  # (c_v_name, g_v_name)
            self.ops.append(('add', op_vs))  # update op
            self.vs_name_of_out_es.append(op_vs)
            new_community.add_edge(*op_vs)
        else:
            if_continue = False
        return if_continue, group, new_community

    def run(self, comm: ig.Graph, group: ig.Graph):
        max_budget = group.vcount() + (group.ecount() - (group.vcount() - 1))  # max budget
        if self.budget > max_budget:
            self.budget = max_budget
        new_comm = self.first_add_out_edge(comm, group)
        while True:
            # print("op {}: {}, {} -> score: {}".format(len(self.ops), *self.ops[-1], self.score[-1]))
            if len(self.ops) >= self.budget:
                break
            op_name, op_vs = self.select_op(comm, group)
            if_continue, group, new_comm = self.execute_op(group, new_comm, op_name, op_vs)
            self.score.append(self.cal_score(comm, group))
            if not if_continue:
                break
        # ig.plot(new_comm, "../data/result/new_community_final.pdf")  # save plot.pdf
        # ig.plot(group, "../data/result/group_final.pdf")
        # print("sub modular: {}".format(sub_modular(self.score)))
        # print("hiding done with {} ops".format(len(self.ops)))
        return self.ops


if __name__ == '__main__':
    greedy_search = GreedySearch(INF_BUDGET, 0)  # instant
    c, g = graph_load.load_graph_gml("../data/lesmis.gml", 'c-'), graph_load.create_full_graph(5, 'g-')  # load data
    # ig.plot(c, "../data/result/community_init.pdf")
    # ig.plot(g, "../data/result/group_init.pdf")
    print("group: ({} vs, {} es); comm: ({} vs, {} es)".format(g.vcount(), g.ecount(), c.vcount(), c.ecount()))
    ops = greedy_search.run(c.copy(), g.copy())  # hiding
    disperse, hidden_score = graph_cal.cal_hidden_score(c, g, ops)  # metrics
    print("group in cluster({}): {}".format(hidden_score, disperse))
    print("ok")
