#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys

sys.path.append('../Python')

import model


# In[2]:


import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import random
import statistics


# Some invariant parameters for this notebook:

## Population parameters:
base_params = {
    # Node parameter
    'A' : 0.0, # Now this will vary case by case.
    
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


# $p^*$ has been chosen because it exposes the effects of the
# Watts-Strogatz structure.
# With $K = 4$, roughly one edge for every node is rewired,
# with the rest comprising the circle lattice.

# In[4]:


p_star = 0.256
K = 4

# N = 2000  --- allowing this to vary now


# This time, run the model with no contact tracing at all.

# In[5]:


def ws_case_generator(N, K, p_star):
    def wscg(**kwargs):
        return model.watts_strogatz_case_p_star(N, K, p_star, **kwargs)
    
    return wscg


# In[6]:


conditions = {
    'A-0.00' : {'A' : 0.00},
    'A-0.05' : {'A' : 0.05},
    'A-0.10' : {'A' : 0.10},
    'A-0.15' : {'A' : 0.15},
    'A-0.20' : {'A' : 0.20},
    'A-0.25' : {'A' : 0.25},
    'A-0.30' : {'A' : 0.30},
    'A-0.35' : {'A' : 0.35},
    'A-0.40' : {'A' : 0.40},
    'A-0.45' : {'A' : 0.45},
    'A-0.50' : {'A' : 0.50},
    'A-0.55' : {'A' : 0.55},
    'A-0.60' : {'A' : 0.60},
    'A-0.65' : {'A' : 0.65},
    'A-0.70' : {'A' : 0.70},
    'A-0.75' : {'A' : 0.75},
    'A-0.80' : {'A' : 0.80},
    'A-0.85' : {'A' : 0.85},
    'A-0.90' : {'A' : 0.90},
    'A-0.95' : {'A' : 0.95},
    'A-1.00' : {'A' : 1.00},
}


# In[7]:


def dfr(rs):
    return pd.DataFrame(
        [r for case in rs 
         for r in model.data_from_results(rs, case)])


# In[8]:


runs = 2

N_cases = [1000, 2000, 4000, 8000]

# In[9]:

for N in N_cases:
    rs = model.experiment(
        ws_case_generator(N, K, p_star),
        base_params,
        conditions,
        runs)

    dfr(rs).to_csv(f'data_{N}.csv')
    del rs

data = pd.concat([
    pd.read_csv(f'data_{N}.csv')
    for N
    in N_cases
])

data.to_csv(f"adoption-study-results-r-{runs}.csv")
