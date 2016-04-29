#!/usr/bin/env python

import csv
import re
import networkx as nx
from data.events import CooperateEventCodes, DisapproveEventCodes


CSV_FILE = 'data/denounce-praise-2.csv'

COOPERATE_REGEXP = re.compile(r"^05")
DISAPPROVE_REGEXP = re.compile(r"^11")
GOV_ACTOR_KEY = "Actor1Name"
BIZ_ACTOR_KEY = "Actor2Name"
GOV_ACTOR_TYPE = "GOV"
BIZ_ACTOR_TYPE = "BIZ"


def is_event_type(pattern):
    def is_event_type_wrapped(event_code):
        return pattern.match(event_code) is not None

    return is_event_type_wrapped


is_cooperate_event = is_event_type(COOPERATE_REGEXP)
is_disapprove_event = is_event_type(DISAPPROVE_REGEXP)


def gdelt_data_iter():
    with open(CSV_FILE, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        header_row = reader.next()
        for row in reader:
            yield dict(zip(header_row, row))


ACTOR_COLS = ["Type1Code", "Name"]


def get_actor_attrs(prefix):
    actor_cols = [prefix + col for col in ACTOR_COLS]

    def get_actor_attrs_wrapped(row):
        return dict(zip(actor_cols, [row.get(col) for col in actor_cols]))

    return get_actor_attrs_wrapped


get_gov_attrs = get_actor_attrs("Actor1")
get_biz_attrs = get_actor_attrs("Actor2")


def integrate_row(graph, event, event_code):
    gov_actor = event.get(GOV_ACTOR_KEY).strip()
    biz_actor = event.get(BIZ_ACTOR_KEY).strip()
    tone = float(event.get("consolidatedAvgTone"))
    eventCount = int(event.get("eventCount"))

    gov_attrs = get_gov_attrs(event)
    gov_attrs['type'] = GOV_ACTOR_TYPE
    gov_node = graph.add_node(gov_actor, **gov_attrs)
    biz_attrs = get_biz_attrs(event)
    biz_attrs['type'] = BIZ_ACTOR_TYPE
    biz_node = graph.add_node(biz_actor, **biz_attrs)
    graph.add_edge(gov_actor, biz_actor, tone=tone,
                   event_code=event_code)

    # Add the weight
    if not graph[gov_actor][biz_actor].get("weight"):
        graph[gov_actor][biz_actor]["weight"] = 0
    graph[gov_actor][biz_actor]["weight"] += eventCount


def build_graph(events_iter):
    disapprove = nx.DiGraph()
    cooperate = nx.DiGraph()

    for event in events_iter:
        event_code = event.get("EventCode")
        if is_disapprove_event(event_code):
            integrate_row(disapprove, event, event_code)
        elif is_cooperate_event(event_code):
            integrate_row(cooperate, event, event_code)

    return disapprove, cooperate


def find_max_degree(func_type):
    def find_max_degree_wrapped(graph):
        if (func_type == "out"):
            degree_func = graph.out_degree
        elif func_type == "in":
            degree_func = graph.in_degree
        max_degree = None
        max_node = None
        for node in graph:
            degree = degree_func(node)
            if degree > max_degree or max_degree is None:
                max_degree = degree
                max_node = node
        return max_node
    return find_max_degree_wrapped


find_out_degree_max = find_max_degree("out")
find_in_degree_max = find_max_degree("in")


GRAPH_SETTINGS = {
    # "dim": 10,
    "k": 0.01,
    "iterations": 100
}
EDGE_SETTINGS = {
    "alpha": 0.5,
    "arrows": False
}


def scale_weight(val, min_val, max_val):
    return float(val - min_val) / (max_val - min_val)


def draw_graph(graph, name, gov_out_degree=1):
    import matplotlib.pyplot as plt

    gov_nodes = [
        node for (node, data) in graph.nodes(data=True)
        if data['type'] == GOV_ACTOR_TYPE and
        graph.out_degree(node) > gov_out_degree
    ]

    print("Filtered %s --\n\tGov Nodes: %d" %
          (name, len(gov_nodes)))

    biz_nodes = []
    for node in gov_nodes:
        biz_nodes += graph.successors(node)

    print("\tBiz Nodes: %d" % (len(biz_nodes)))

    # pos = nx.spring_layout(graph, **GRAPH_SETTINGS)
    pos = nx.fruchterman_reingold_layout(graph, **GRAPH_SETTINGS)

    # Size gov nodes by out degree
    out_degrees = graph.out_degree(nbunch=gov_nodes)
    nx.draw_networkx_nodes(graph, pos, nodelist=gov_nodes, node_color='m',
                           node_size=[val for val in out_degrees.values()])

    # Size biz nodes by in degree
    in_degrees = graph.in_degree(nbunch=biz_nodes)
    nx.draw_networkx_nodes(graph, pos, nodelist=biz_nodes, node_color='c',
                           node_size=[val for val in in_degrees.values()])

    # Filter to only edges connected to gov nodes
    all_edges = graph.edges(nbunch=gov_nodes, data=True)
    # Separate the edges with negative and positive tone (stored as weight)
    edges_positive = [(u, v, d) for (u, v, d) in all_edges if d['tone'] >= 0.0]
    positive_weights = [d["weight"] for (u, v, d) in edges_positive]
    pos_min = min(positive_weights)
    pos_max = max(positive_weights)
    edges_positive_weights = [scale_weight(d["weight"], pos_min, pos_max) * 2
                              for (u, v, d) in edges_positive]

    edges_negative = [(u, v, d) for (u, v, d) in all_edges if d['tone'] < 0.0]

    negative_weights = [d["weight"] for (u, v, d) in edges_negative]
    neg_min = min(negative_weights)
    neg_max = max(negative_weights)
    edges_negative_weights = [scale_weight(d["weight"], neg_min, neg_max) * 2
                              for (u, v, d) in edges_negative]

    # Draw positive tone edges in blue
    nx.draw_networkx_edges(graph, pos, edgelist=edges_positive, edge_color='b',
                           width=edges_positive_weights, **EDGE_SETTINGS)
    # Draw negative tone edges in green
    nx.draw_networkx_edges(graph, pos, edgelist=edges_negative, edge_color='g',
                           width=edges_negative_weights, **EDGE_SETTINGS)

    # labels
    labels = {node: node for node in gov_nodes}
    nx.draw_networkx_labels(graph, pos, labels=labels, font_size=5)

    plt.axis('off')
    plt.savefig("results/%s_weighted_graph.pdf" % (name))


def node_labels(graph):
    [n for n in graph.nodes()]


def main():
    disapprove, cooperate = build_graph(gdelt_data_iter())

    print("Disapprove --\n\tNodes: %d\n\tEdges: %d" %
          (disapprove.order(), disapprove.size()))
    print("Cooperate --\n\tNodes: %d\n\tEdges: %d" %
          (cooperate.order(), cooperate.size()))

    draw_graph(disapprove, "disapprove", gov_out_degree=10)
    draw_graph(cooperate, "cooperate", gov_out_degree=10)

    max_out_disagree = find_out_degree_max(disapprove)
    print("Most disapproving government with business: %s" % max_out_disagree)
    max_in_disagree = find_in_degree_max(disapprove)
    print("Most disapproved business by government: %s" % max_in_disagree)

    max_out_cooperate = find_out_degree_max(cooperate)
    print("Most cooperative government with business: %s" % max_out_cooperate)
    max_in_cooperate = find_in_degree_max(cooperate)
    print("Most cooperative business by government: %s" % max_in_cooperate)


if __name__ == "__main__":
    main()
