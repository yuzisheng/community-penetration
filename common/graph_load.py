import igraph as ig


def load_graph_gml(file_path: str, vertex_name_prefix: str) -> ig.Graph:
    """ load graph in gml format (rename if the attribute of 'name' exists) """
    # g = ig.load(file_path, format='gml')
    g = ig.Graph.Read_GML(file_path)
    g.vs['name'] = [vertex_name_prefix + str(i) for i in range(g.vcount())]
    return g


def load_graph_txt(file_path: str, vertex_name_prefix: str) -> ig.Graph:
    """ .txt: each record of file has the format of [source-vertex, target-vertex] """
    g = ig.Graph.Read_Edgelist(file_path, directed=False)
    g.vs['name'] = [vertex_name_prefix + str(_) for _ in range(g.vcount())]
    return g


def create_full_graph(k: int, vertex_name_prefix: str) -> ig.Graph:
    """ create complete graph """
    g = ig.Graph.Full(k)
    g.vs['name'] = [vertex_name_prefix + str(i) for i in range(k)]
    return g


def create_star_graph(k: int, vertex_name_prefix: str) -> ig.Graph:
    """ create star graph """
    g = ig.Graph.Star(k)
    g.vs['name'] = [vertex_name_prefix + str(i) for i in range(k)]
    return g


def create_multi_tree(children: int, depth: int, vertex_name_prefix: str) -> ig.Graph:
    """ create multi tree like binary tree graph or line graph """
    num_vertices = int((1 - pow(children, depth + 1)) / (1 - children)) if children != 1 else depth + 1
    g = ig.Graph.Tree(num_vertices, children)
    g.vs['name'] = [vertex_name_prefix + str(i) for i in range(g.vcount())]
    return g


def create_barabasi_albert_graph(num_v: int, num_e_of_each_vertex: int, vertex_name_prefix: str) -> ig.Graph:
    """ create a graph based on the Barabasi-Albert model """
    g = ig.Graph.Barabasi(num_v, num_e_of_each_vertex)
    g.vs['name'] = [vertex_name_prefix + str(i) for i in range(g.vcount())]
    return g


def union_two_graphs(g1: ig.Graph, g2: ig.Graph) -> ig.Graph:
    """ union two graphs to one (assume that graph has attribute of 'name')"""
    union_g = ig.Graph()
    union_g.add_vertices(g1.vs['name'])
    for e in g1.es:
        source, target = g1.vs[e.source]['name'], g1.vs[e.target]['name']
        union_g.add_edge(source, target)
    union_g.add_vertices(g2.vs['name'])
    for e in g2.es:
        source, target = g2.vs[e.source]['name'], g2.vs[e.target]['name']
        union_g.add_edge(source, target)
    return union_g


if __name__ == '__main__':
    k_graph = create_full_graph(3, 'node-')
    multi_tree = create_multi_tree(2, 3, 'node-')
    print("ok")
