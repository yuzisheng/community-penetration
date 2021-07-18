from baseline.random_algo import RandomAlgo
from common import graph_load, graph_cal

if __name__ == '__main__':
    c = graph_load.load_graph_gml("../data/lesmis.gml", 'c-')
    g = graph_load.create_full_graph(5, 'g-')
    random_algo = RandomAlgo(10000)
    ops = random_algo.run(g, c, budget=6, conv_rate=0)
    print("ops: {}, {}".format(ops, graph_cal.cal_hidden_score(g, c, ops)))
    print("ok")
