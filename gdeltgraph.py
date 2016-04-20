#!/usr/bin/env python

import csv
import re
import networkx as nx

from data.events import CooperateEventCodes, DisapproveEventCodes


CSV_FILE = 'data/denounce_praise.csv'

COOPERATE_REGEXP = re.compile(r"^05")
DISAPPROVE_REGEXP = re.compile(r"^11")


GOV_ACTOR_KEY = "Actor1Code"
BIZ_ACTOR_KEY = "Actor2Code"


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
    gov_actor = event.get(GOV_ACTOR_KEY)
    biz_actor = event.get(BIZ_ACTOR_KEY)
    tone = event.get("consolidatedAvgTone")

    gov_node = graph.add_node(gov_actor, **get_gov_attrs(event))
    biz_node = graph.add_node(biz_actor, **get_biz_attrs(event))
    graph.add_edge(gov_actor, biz_actor, weight=tone, event_code=event_code)


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


def main():
    disapprove, cooperate = build_graph(gdelt_data_iter())

    print("Disapprove --\n\tNodes: %d\n\tEdges: %d" %
          (disapprove.order(), disapprove.size()))
    print("Cooperate --\n\tNodes: %d\n\tEdges: %d" %
          (cooperate.order(), cooperate.size()))


if __name__ == "__main__":
    main()
