#https://stackoverflow.com/questions/49429368/how-to-solve-memory-issues-problems-while-multiprocessing-using-pool-map

#https://pypi.org/project/memory-profiler/

import cProfile

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import random
import seaborn as sns
import statistics

import sys

sys.path.append('.')

import model



## Population parameters:
base_params = {
    # Node parameter
    'A' : 0.5, # Now this will vary case by case.

    # Edge parameter
    'W' : .5, # probability of edge activation; 2/K
    'C' : 1.0, ## all edges can be traced.

    ## Disease parameters

    'beta_hat' : .4, # probability of transmission upon contact
    'alpha' : .25, # probability of exposed becoming infectious
    'gamma' : .1, # probability of infectious becoming recovered
    'zeta' : .1, # probability of infectious becoming symptomatic

    ## Contact tracing parameters

    'limit' : 10, # number of time steps the contact tracing system remembers
}

p_star = 0.256
K = 4
N = 2000

conditions = {
    'A-0.10' : {'A' : 0.10},
    'A-0.30' : {'A' : 0.30},
    'A-0.50' : {'A' : 0.50},
    'A-0.70' : {'A' : 0.70}
}

def watts_strogatz_case_p_star(N, K, p_star, **kwargs):

    g = nx.watts_strogatz_graph(N, K, p_star)

    g.graph['N'] = N
    g.graph['K'] = K
    g.graph['p'] = p_star

    return g, kwargs

def ws_case_generator(N, K, p_star):
    def wscg(**kwargs):
        return watts_strogatz_case_p_star(N, K, p_star, **kwargs)

    return wscg

def test():

    runs = 8

    results = model.experiment(
        ws_case_generator(N, K, p_star),
        base_params,
        conditions,
        runs)

    pd.DataFrame(results).to_csv('data_test.csv')


if __name__ == '__main__':
    test()
