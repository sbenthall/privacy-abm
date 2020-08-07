## python

from collections import defaultdict
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import random


## Setup utilities

def expected_one_per_edge(g, e):
    return len(g.nodes()) / len(g.edges())

def local_density(g, e):
    u, v, d = e
    
    u_neighbors = set(nx.neighbors(g, u))
    v_neighbors = set(nx.neighbors(g, v))
    
    common_neighbors = set(u_neighbors).intersection(v_neighbors)
    all_neighbors = set(u_neighbors).union(v_neighbors)
    
    return len(common_neighbors) / len(all_neighbors)

## 0. Initialize the model

def initialize_weights(g, params):
    if type(params['W']) is float:
        nx.set_edge_attributes(g, params['W'], name = 'w')
    elif callable(params['W']):
        nx.set_edge_attributes(g,
                               {
                                   (e[0], e[1]) : params['W'](g, e)
                                   for e
                                   in g.edges(data = True)
                               },
                               name = 'w')
    else:
        print("No case found for Weight type.")
        pass

def initialize_tracing_probability(g, params):
    if type(params['C']) is float:
        nx.set_edge_attributes(g, params['C'], name = 'c')
    elif callable(params['C']):
        nx.set_edge_attributes(g,
                               {
                                   (e[0], e[1]) : params['C'](g, e)
                                   for e
                                   in g.edges(data = True)
                               },
                               name = 'c')
    else:
        print("No case found for traCing probability type.")
        pass

def initialize_adopters(g, params, how='bernoulli'):
    if how == 'bernoulli':
        nx.set_node_attributes(
            g,
            {x : np.random.random() < params['A'] for x in g.nodes()},
            name = 'adopter')
    else:
        pass

def initialize_state(g):
    nx.set_node_attributes(
        g,
        False,
        name = 'quarantined')

    nx.set_node_attributes(
        g,
        False,
        name = 'symptomatic')

    nx.set_node_attributes(
        g,
        False,
        name = 'tested')

def initialize_epi_states(g):
    nx.set_node_attributes(
        g,
        "Susceptible",
        name = 'epi-state')

    nx.set_node_attributes(
        g,
        {
            random.choice(list(g.nodes())) :
            {
                'epi-state' : 'Infectious'
            }
        }
    )

def initialize(g,params):
    initialize_weights(g, params)
    initialize_tracing_probability(g, params)
    initialize_adopters(g, params)
    initialize_state(g)
    initialize_epi_states(g)

## 1. Choose activated edges

def quarantined(g, edge):
    return g.nodes[edge[0]]['quarantined'] or g.nodes[edge[1]]['quarantined']


def active_edges(g, weight_attr = 'w'):
    return [
        edge
        for edge
        in g.edges(data=True)
        if not quarantined(g, edge)
        and np.random.random() <= edge[2][weight_attr]
    ]
    

## 2.a. Trace along active edge

## Can implement more flexible adoption logic later if need be...
def adoption(g, edge):
    return g.nodes[edge[0]]['adopter'] and g.nodes[edge[1]]['adopter']

def traced_contacts(g, active_edges, history, t):
    contact_history = defaultdict(lambda : set())
    
    for edge in active_edges:
        if adoption(g, edge):
            if np.random.random() <= edge[2]['c']:
                contact_history[edge[0]].add(edge[1])
                contact_history[edge[1]].add(edge[0])
    
    history[t] = contact_history

    return contact_history
    

## 2.a. Infections along active edge
    
def infections(g, active_edges, beta_hat = .5, copy = True):
    if copy:
        g = g.copy()
        
    for edge in active_edges:
        if g.nodes[edge[0]]['epi-state'] == 'Infectious' \
        and g.nodes[edge[1]]['epi-state'] == 'Susceptible':
            if np.random.random() <= beta_hat:
                nx.set_node_attributes(
                    g,
                    { edge[1] :
                     {'epi-state' : 'Exposed'}
                    }
                )
        elif g.nodes[edge[1]]['epi-state'] == 'Infectious' \
        and g.nodes[edge[0]]['epi-state'] == 'Susceptible':
            if np.random.random() <= beta_hat:
                nx.set_node_attributes(
                    g,
                    { edge[0] :
                     {'epi-state' : 'Exposed'}
                    }
                )
    
    return g


## 3 Disease progression

def progress_disease(g, t, alpha = .25, gamma = .1, copy = True):
    if copy:
        g = g.copy()
    
    for node, data in g.nodes(data=True):
        if data['epi-state'] == 'Exposed':
            if np.random.random() < alpha:
                nx.set_node_attributes(
                    g,
                    {node : {
                        'epi-state' : 'Infectious'
                    }}
                )

        if data['epi-state'] == 'Infectious':
            if np.random.random() < gamma:
                nx.set_node_attributes(
                    g,
                    {node : {
                        'epi-state' : 'Recovered',
                        'recovered-at' : t
                    }}
                )
        
    return g

## 4.a Become symptomatic

def symptomaticity(g, history, t, zeta = .1, limit = 10, copy = True):
    if copy:
        g = g.copy()
    
    for node, data in g.nodes(data=True):
        if data['epi-state'] == 'Infectious':
            if np.random.random() < zeta:
                nx.set_node_attributes(
                    g,
                    {node : {
                        'symptomatic' : True,
                    }}
                )
                g = get_tested(node, g, history, t, copy = copy)
        
    return g


## 4.b Get tested


def get_tested(node, g, history, t, limit = 10, copy = True):
    if g.nodes[node]['tested']:
        return g
    
    if copy:
        g = g.copy()
    
    g.nodes[node]['tested'] = True
    epi_state = g.nodes[node]['epi-state']
    
    if epi_state == 'Exposed' or epi_state == 'Infectious':
        ## TESTING POSITIVE!
        g.nodes[node]['quarantined'] = True
        g.nodes[node]['quarantined-at'] = t

        for t_past in range(max(0, t - limit), t + 1):
            if node in history[t_past]:
                for contact in history[t_past][node]:
                    g = get_tested(contact,
                                   g,
                                   history,
                                   t,
                                   copy = copy)
        
        return g
    else:
        ## negative. Do nothing.
        return g


## 5. Clear the tested flags

def clear_testing(g, copy=True):
    if copy:
        g = g.copy()
        
    nx.set_node_attributes(
        g,
        False,
        name = 'tested'
    )
    
    return g


### PUTTING IT ALL TOGETHER

def get_infected(g):
    return [n
            for n 
            in g.nodes(data=True) 
            if n[1]['epi-state'] == 'Infectious']

def loop(params, g, history, t, copy = True):
    if copy:
        g = g.copy()
        history = history.copy()
        
    ae = active_edges(g)
    tc = traced_contacts(g,
                         ae,
                         history,
                         t)

    g = infections(g,
                   ae,
                   beta_hat = params['beta_hat'],
                   copy = False)

    g = progress_disease(g,
                         t,
                         alpha = params['alpha'],
                         gamma = params['gamma'],
                         copy = False)
    
    g = symptomaticity(g,
                       history,
                       t,
                       zeta = params['zeta'],
                       limit = params['limit'],
                       copy = False)

    g = clear_testing(g, copy = False)
    
    return g, history


### Running an experiment


def simulate_sample(g, params, runs, time_limit = float("inf")):

    records = []

    for i in range(runs):
        if i % 100 == 0:
            print("Trial %d" % (i))

        t = 0
        g_live = g.copy()
        initialize(g_live,params)
        history = {}

        s_count = []
        
        while len(get_infected(g_live)) > 0 and t < time_limit:
            if t != 0 and t % 100 == 0:
                print("Trial %d hits time step %d" % (i,t))

            s_count.append(len(susceptible(g_live)))

            g_live, history = loop(params, g_live, history, t)

            t = t + 1

        records.append((t, g_live.copy(), history.copy(), s_count))

    return records

def experiment(generator, conditions : dict, runs):
    """
    generator: takes keyword arguments and returns a graph and params dict
    conditions: a dictionary of dictionaries, with the keyword arguments
    runs: the number of runs per condition
    """
    results = {}

    for case in conditions:

        g, params = generator(**conditions[case])

        print(case)
        results[case] = simulate_sample(
            g,
            params,
            runs
        )

    return results

def experiment_on_graph(g, conditions : dict, runs):
    results = {}

    for case in conditions:
        print(case)
        results[case] = simulate_sample(
            g,
            conditions[case],
            runs
        )

    return results

### Measuring output

def susceptible(g):
    return [n
            for n 
            in g.nodes(data=True) 
            if n[1]['epi-state'] == 'Susceptible']

### Visualization

green_cmap = plt.get_cmap('Greens')
orange_cmap = plt.get_cmap('Oranges')

grey_cmap = plt.get_cmap('Greys')

def node_colors(g):
    node_color = [
        orange_cmap(n[1]['quarantined-at'])
        if n[1]['quarantined']
        else green_cmap(n[1]['recovered-at'])
        if n[1]['epi-state'] == 'Recovered'
        else 'r'
        if n[1]['epi-state'] == 'Infectious'
        else 'y'
        if n[1]['epi-state'] == 'Exposed'
        else 'c'
        if n[1]['epi-state'] == 'Susceptible' and n[1]['adopter']
        else 'b'
        for n
        in g.nodes(data=True)
    ]

    return node_color

def edge_colors(g):
    edge_color = [
        (e[2]['w'], e[2]['c'], 1 - e[2]['w'] * e[2]['c'] )
        for e
        in g.edges(data=True)
    ]

    return edge_color
