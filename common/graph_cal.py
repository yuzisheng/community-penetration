import igraph as ig
import _pickle as pickle
from common.constant import BASE_WEIGHT
from common import graph_load


def cal_convenience_of_graph(g: ig.Graph) -> float:
    """ cal avg closeness of graph and normalize it """
    return sum(g.closeness()) / len(g.closeness())


def cal_as_of_vertex(g: ig.Graph, vertex_name: str) -> float:
    """ cal the attraction of a graph to a vertex """
    vertex_idx = g.vs.find(vertex_name).index  # find edges or vertices using index instead of name
    as_of_v = 0
    # first layer search
    weight = 1/2  # init weight
    first_layer_edges = g.incident(vertex_idx)
    vertices_to_search = g.neighbors(vertex_idx)
    edges_searched = {_ for _ in first_layer_edges}
    vertices_searched = {vertex_idx}
    as_of_v += (len(first_layer_edges) * weight)
    # loop to traverse all edges
    while True:
        # print("# search vertices: {}".format([g.vs['name'][_] for _ in vertices_to_search]))
        weight *= BASE_WEIGHT  # weight decrease with higher layer
        next_layer_edges = []  # store adjacent edges of vertices (allow to duplicate)
        next_layer_vertices = []  # store neighbors vertices of vertices (allow to duplicate)
        for v in vertices_to_search:
            next_layer_edges.extend(g.incident(v))
            next_layer_vertices.extend(g.neighbors(v))
            vertices_searched.add(v)  # update vertices already searched
        as_of_v += (weight * len(set(next_layer_edges) - edges_searched))  # weighted summation for new edges
        vertices_to_search = list(set(next_layer_vertices) - vertices_searched)  # update candidate vertices to search
        edges_searched = edges_searched.union(set(next_layer_edges))  # update edges already searched
        if len(edges_searched) == g.ecount():
            break
    return as_of_v


def cal_safeness_of_graph(g: ig.Graph) -> float:
    """ cal safeness of graph: looseness of the graph (inverse to attraction) """
    num_v = g.vcount()
    # complete graph
    # max_avg_as = cal_as_of_vertex(graph_load.create_full_graph(num_v, 'complete-'), 'complete-0')
    max_avg_as = (num_v - 1) * 1 + (num_v * (num_v - 1) / 2 - (num_v - 1)) * BASE_WEIGHT
    # line graph
    min_avg_as = sum([cal_as_of_vertex(graph_load.create_multi_tree(
        1, num_v - 1, 'line-'), 'line-' + str(_)) for _ in range(num_v)]) / num_v
    avg_as = sum([cal_as_of_vertex(g, v_name) for v_name in g.vs['name']]) / num_v
    norm_avg_as = (avg_as - min_avg_as) / (
            max_avg_as - min_avg_as) if num_v != 2 else 0
    return 1 - norm_avg_as


def cal_hidden_score(group: ig.Graph, community: ig.Graph, ops: list) -> (list, float):
    """ cal hidden score: [0, 1] """
    new_comm = graph_load.union_two_graphs(community, group)
    for op in ops:
        new_comm.add_edge(*op[1]) if op[0] == 'add' else new_comm.delete_edges([op[1]])
    cluster_c = new_comm.community_leading_eigenvector()
    # cluster_c = new_comm.community_label_propagation()
    # ig.plot(cluster_c, "../data/result/community_with_group_cluster.pdf")
    clusters = [sub_graph.vs['name'] for sub_graph in cluster_c.subgraphs()]
    print("clusters: {}".format(len(clusters)))
    group_vs = group.vs['name']
    g_clusters = []
    for cluster in clusters:
        num_in_cluster = len([_ for _ in cluster if _ in group_vs])
        if num_in_cluster:
            g_clusters.append((num_in_cluster, len(cluster)))
    # hidden_score = 1 - sum([(i[0] / i[1]) * (i[0] / group.vcount()) for i in g_cluster]) / len(g_cluster)
    hidden_score = 1 - sum([(i[0] / i[1]) * (i[0] / group.vcount()) for i in g_clusters])
    return g_clusters, hidden_score


def gen_groups_of_graph(g: ig.Graph):
    clusters = g.community_leading_eigenvector()
    subs = []
    for sub_graph in clusters.subgraphs():
        sub_comm = g.copy()
        sub_comm.delete_vertices([_['name'] for _ in sub_graph.vs])
        sub_comm.vs['name'] = ['c-' + str(i) for i in range(sub_comm.vcount())]  # rename
        sub_graph.vs['name'] = ['g-' + str(i) for i in range(sub_graph.vcount())]
        subs.append((sub_comm, sub_graph))
    return subs


def gen_min_max_as_file():
    """ pre generate the file of min-max-as value """
    min_max_as = {}
    for num_v in range(2, 500):
        max_avg_as = cal_as_of_vertex(graph_load.create_full_graph(num_v, 'complete-'), 'complete-0')
        min_avg_as = sum([cal_as_of_vertex(graph_load.create_multi_tree(
            1, num_v - 1, 'line-'), 'line-' + str(_)) for _ in range(num_v)]) / num_v
        min_max_as[num_v] = (min_avg_as, max_avg_as)
        print("cal {} done".format(num_v), end='\r', flush=True)
    with open("../data/pre/min_max_as.pkl", "wb") as fw:
        pickle.dump(min_max_as, fw)
    print("gen min_max_as_file done")


if __name__ == '__main__':
    # gen_min_max_as_file()
    # with open("../data/pre/min_max_as.pkl", "rb") as fr: print(pickle.load(fr))

    # k_graph = graph_load.create_full_graph(3, 'node-')  # complete graph
    # print("complete graph safeness: {}".format(cal_safeness_of_graph(k_graph)))
    # print(k_graph.closeness(), cal_convenience_of_graph(k_graph))

    # multi_tree = graph_load.create_multi_tree(1, 2, 'node-')  # line graph
    # print("line graph safeness: {}".format(cal_safeness_of_graph(multi_tree)))
    # print(multi_tree.closeness(), cal_convenience_of_graph(multi_tree))

    lesmis = graph_load.load_graph_gml("../data/lesmis.gml", 'c-')
    gen_groups_of_graph(lesmis)

    print("ok")
