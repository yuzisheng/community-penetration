import igraph as ig
from common import graph_load, graph_cal


def comm_detection(g: ig.Graph):
    g.community_walktrap()


if __name__ == '__main__':
    # 1. lesmis
    lesmis = graph_load.load_graph_gml("../data/lesmis.gml", 'c-')
    print("+++++++\nlesmis: (v:{}, e:{}) conv:{}".format(lesmis.vcount(), lesmis.ecount(),
                                                         graph_cal.cal_convenience_of_graph(lesmis)))
    # 2. karate
    karate = graph_load.load_graph_gml("../data/karate.gml", 'c-')
    print("+++++++\nkarate: (v:{}, e:{}) conv:{}".format(karate.vcount(), karate.ecount(),
                                                         graph_cal.cal_convenience_of_graph(karate)))
    # 3. football
    football = graph_load.load_graph_gml("../data/football.gml", 'c-')
    print("+++++++\nfootball: (v:{}, e:{}) conv:{}".format(football.vcount(), football.ecount(),
                                                           graph_cal.cal_convenience_of_graph(football)))
    # 4. political books
    polb = graph_load.load_graph_txt("../data/political-books.txt", 'c-')
    print("+++++++\npolb: (v:{}, e:{}) conv:{}".format(polb.vcount(), polb.ecount(),
                                                       graph_cal.cal_convenience_of_graph(polb)))
    # 5. email
    email = graph_load.load_graph_txt("../data/email-Eu-core.txt", 'c-')
    print("+++++++\nemail: (v:{}, e:{}) conv:{}".format(email.vcount(), email.ecount(),
                                                        graph_cal.cal_convenience_of_graph(email)))
    # 6. mad
    mad = graph_load.load_graph_txt("../data/mad.txt", 'c-')
    print("+++++++\nmad: (v:{}, e:{}) conv:{}".format(mad.vcount(), mad.ecount(),
                                                      graph_cal.cal_convenience_of_graph(mad)))
    ig.plot(mad, "../data/result/mad.pdf")

    print("ok")
