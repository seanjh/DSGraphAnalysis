#!/usr/bin/env python

import csv
import networkx as nx

from data.events import CooperateEventCodes, DisapproveEventCodes


CSV_FILE = 'data/denounce_praise.csv'


def gdelt_data_iter():
    with open(CSV_FILE, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        header_row = reader.next()
        for row in reader:
            yield dict(zip(header_row, row))


def main():
    for row in gdelt_data_iter():
        pass


if __name__ == "__main__":
    main()
