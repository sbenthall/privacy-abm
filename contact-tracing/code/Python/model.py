## python

from collections import defaultdict
import networkx as nx
import numpy as np
import random

## 0. Initialize the model

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
