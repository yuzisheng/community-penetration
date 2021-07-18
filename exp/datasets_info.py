import igraph as ig
from common import graph_load, graph_cal


def comm_detection(g: ig.Graph):
    g.community_walktrap()


if __name__ == '__main__':
    # 1. karate
    karate = graph_load.load_graph_gml("../data/karate.gml", 'c-')
    print("+++++++\nkarate: (v:{}, e:{})".format(karate.vcount(), karate.ecount()))
    print("# of communities(eig): {}".format(len(karate.community_leading_eigenvector())))
    print("# of communities(lab): {}".format(len(karate.community_label_propagation())))
    # print("# of communities(opt): {}".format(len(karate.community_optimal_modularity())))
    # print("# of communities(inf): {}".format(len(karate.community_infomap())))
    # print("# of communities(spin): {}".format(len(karate.community_spinglass())))

    # 2. dolphins
    dol = graph_load.load_graph_gml("../data/dolphins.gml", 'c-')
    print("+++++++\npolb: (v:{}, e:{})".format(dol.vcount(), dol.ecount()))
    print("# of communities(eig): {}".format(len(dol.community_leading_eigenvector())))
    print("# of communities(lab): {}".format(len(dol.community_label_propagation())))

    # 3. lesmis
    lesmis = graph_load.load_graph_gml("../data/lesmis.gml", 'c-')
    print("+++++++\nlesmis: (v:{}, e:{})".format(lesmis.vcount(), lesmis.ecount()))
    print("# of communities(eig): {}".format(len(lesmis.community_leading_eigenvector())))
    print("# of communities(lab): {}".format(len(lesmis.community_label_propagation())))

    # 4. political books
    polb = graph_load.load_graph_txt("../data/political-books.txt", 'c-')
    print("+++++++\npolb: (v:{}, e:{})".format(polb.vcount(), polb.ecount()))
    print("# of communities(eig): {}".format(len(polb.community_leading_eigenvector())))
    print("# of communities(lab): {}".format(len(polb.community_label_propagation())))

    # 5. football
    football = graph_load.load_graph_gml("../data/football.gml", 'c-')
    print("+++++++\nfootball: (v:{}, e:{})".format(football.vcount(), football.ecount()))
    print("# of communities(eig): {}".format(len(football.community_leading_eigenvector())))
    print("# of communities(lab): {}".format(len(football.community_label_propagation())))

    # 6. facebook
    facebook = graph_load.load_graph_txt("../data/facebook.txt", 'c-')
    print("+++++++\nfacebook: (v:{}, e:{})".format(facebook.vcount(), facebook.ecount()))
    ig.plot(facebook, "../data/power.pdf")
    print("# of communities(eig): {}".format(len(facebook.community_leading_eigenvector())))
    print("# of communities(lab): {}".format(len(facebook.community_label_propagation())))

    print("ok")
