#!/usr/bin/env python

import os
import networkx as nx
from gdeltgraph import (build_graph, gdelt_data_iter)


def main():
    disapprove, cooperate = build_graph(gdelt_data_iter())

    # Computer pagerank for disapprove Graph node
    print("Computing pagerank for disapprove graph")
    pagerank1 = nx.pagerank_numpy(disapprove, alpha=0.90)
    print("Computing pagerank for cooperate graph")
    pagerank2 = nx.pagerank_numpy(cooperate, alpha=0.90)

    max1 = max(pagerank1.values())

    key1 = ''
    key2 = ''
    for key in pagerank1.keys():
        if pagerank1[key] == max1:
            key1 = key

    max2 = max(pagerank2.values())
    for key in pagerank2.keys():
        if pagerank2[key] == max2:
            key2 = key

    with open('results/disapprove_graph_page_rank.csv', 'w') as f1:
        for line in str(pagerank1):
            f1.write(line)

    with open('results/cooperate_graph_page_rank.csv', 'w') as f2:
        for line in str(pagerank2):
            f2.write(line)

    print("Maximum Page rank for disapprove graph is: %s %s" % (key1, max1))
    print("Maximum Page rank for cooperate graph is:  %s %s" % (key2, max2))

if __name__ == "__main__":
    main()
