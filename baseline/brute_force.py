import igraph as ig
from itertools import product, combinations
from common import graph_cal, graph_load
from common.constant import BASE_WEIGHT


class BruteForce:
    def __init__(self, budget: int, conv_rate: float):
        self.budget = budget
        self.conv_rate = conv_rate

    def cal_safeness_and_conv(self, del_ops: tuple, add_ops: tuple, group: ig.Graph, comm: ig.Graph):
        comm_add_vertices = [_[0] for _ in add_ops]
        group_add_vertices = [_[1] for _ in add_ops]
        # 1. check if add ops are valid
        if len(set(comm_add_vertices)) != len(comm_add_vertices) or len(set(group_add_vertices)) != len(
                group_add_vertices):
            return "duplicated"
        # 2. check if del ops are valid
        group_copy = group.copy()
        for del_op in del_ops:
            group_copy.delete_edges([del_op])
        if group_copy.is_connected():
            # if ops are valid, cal score
            in_score = graph_cal.cal_safeness_of_graph(group_copy)
            convenience = graph_cal.cal_convenience_of_graph(group_copy)
            out_score = 0
            for add_op in add_ops:
                g_v_name, c_v_name = add_op
                in_attraction = graph_cal.cal_as_of_vertex(group_copy, g_v_name)
                out_attraction = 1 + BASE_WEIGHT * comm.degree(c_v_name)
                out_score += (out_attraction / in_attraction)
            return in_score + out_score + self.conv_rate * convenience
        else:
            return 'unconnected'

    def run(self, group: ig.Graph, comm: ig.Graph):
        max_budget = group.vcount() + (group.ecount() - (group.vcount() - 1))  # max budget
        if self.budget > max_budget:
            self.budget = max_budget
        # op_choice = ['add', 'del']
        del_choice = [(group.vs[e.source]['name'], group.vs[e.target]['name']) for e in group.es]  # only existing edges
        comm_top_vertices = [_[0] for _ in sorted([(_['name'], comm.degree(_)) for _ in comm.vs],
                                                  key=lambda x: x[1], reverse=True)[:self.budget]]
        add_choice = list(product(group.vs['name'], comm_top_vertices, repeat=1))  # [g_vs_name, c_vs_name]
        best_score, best_ops = 0, ("del-ops", "add-ops")
        # must have add op
        for add_op_num in range(1, self.budget + 1):
            add_ops_comb = list(combinations(add_choice, add_op_num))
            del_ops_comb = list(combinations(del_choice, self.budget - add_op_num))
            # search max score
            for del_ops in del_ops_comb:
                for add_ops in add_ops_comb:
                    score = self.cal_safeness_and_conv(del_ops, add_ops, group, comm)
                    if score not in ["unconnected", "duplicated"] and score > best_score:
                        best_score = score
                        best_ops = (del_ops, add_ops)
            # print("# searching {} add ops is done".format(add_op_num))
        # ops = [('del', _) for _ in best_ops[0] if len(best_ops[0])] + [
        #     ('add', _) for _ in best_ops[1] if len(best_ops[1])]
        # print("best ops: {}, best score: {}".format(ops, best_score))
        return [('del', _) for _ in best_ops[0] if len(best_ops[0])] + [
            ('add', _) for _ in best_ops[1] if len(best_ops[1])]


if __name__ == '__main__':
    c = graph_load.load_graph_gml("../data/lesmis.gml", 'c-')
    g = graph_load.create_full_graph(5, 'g-')
    brute_force = BruteForce(1, 0)
    res = brute_force.run(g, c)
    print(res)
    print("ok")
