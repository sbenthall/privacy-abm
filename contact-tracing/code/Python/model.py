## python

from collections import defaultdict
import math
import matplotlib.pyplot as plt
import multiprocessing
import networkx as nx
import numpy as np
import pandas as pd
import random
import seaborn as sns
import statistics
import time

## graph utilities

def grid_r(N, M, p):
    '''
    N - height
    M - width
    p - rewiring rate
    '''
    g = nx.grid_2d_graph(N, M, periodic=True, create_using=None)

    g.graph['N'] = N
    g.graph['M'] = M
    g.graph['p'] = p

    for e in g.edges:
        if random.random() <= p:
            g.remove_edge(e[0],e[1])
            v = random.choice(list(g.nodes()))
            g.add_edge(e[0], v)

    return g

def grid_pos(g):
    dummy_g = nx.grid_2d_graph(
        g.graph['N'],
        g.graph['M'],
        periodic=False,
        create_using=None
    )
    pos = nx.spectral_layout(dummy_g)
    return pos

## math utilities

def inflection_point(x, y, rising = False):
    """
    Returns the x, y values of point where first derivative is minimum.
    This approximates the inflection point.
    """

    df1 = np.gradient(y, x, edge_order = 2)

    df2 = np.gradient(df1, x, edge_order = 2)

    ix = np.argsort(df1) ## lowest first

    i = -1 if rising else 0

    return (x[ix[i]],y[ix[i]])


## Setup utilities

def watts_strogatz_case_p_star(N, K, p_star, **kwargs):

    g = nx.watts_strogatz_graph(N, K, p_star)

    g.graph['N'] = N
    g.graph['K'] = K
    g.graph['p'] = p_star

    return g, kwargs

def expected_one_per_edge(g, e):
    return len(g.nodes()) / len(g.edges())

def circle_distance(e, N):
    return min(
        abs(e[0] - e[1]) % N,
        abs(e[1] - e[0] % N)
    )

def square_distance(e, N, M):
    x = circle_distance(
        (e[0][0], e[1][0]), N
    )
    y = circle_distance(
        (e[0][1], e[1][1]), M
    )

    return math.sqrt(x ** 2 + y ** 2)

def latitude(i, N):
    dist_from_north_pole = min(
        i,
        abs(N / 4 - i) # 1/4 here is just rotating, for the drawing
    )
    return N / 4 - dist_from_north_pole

def hemisphere_adoption(mu, delta):
    '''
    Adopt with mean rate mu
    + delta if in the northern hemisphere
    - delta if in the southern hemisphere
    '''
    def hemisphere(g, i):
        N = len(g.nodes())
        i = i[0]
        # distance between u and v > size of original neighborhood / 2
        if g.nodes[i]['group'] == 0:
        #if latitude(i, N) > 0:
            rate = mu + delta
        else:
            rate = mu - delta

        return 1 if np.random.random() < rate else 0

    return hemisphere

def q_knockout(q):
    def knockout(g, e):
        # distance between u and v > size of original neighborhood / 2
        if circle_distance(e, g.graph['N']) > g.graph['K'] / 2:
            return 1.0 if np.random.random() < q else 0.0
        else:
            return 1.0

    return knockout

def qr_knockout(q, r):
    '''
    Allows q of distant edges and r of close edges
    to be be traced (if they are adopted).
    '''
    def knockout(g, e):
        # a distant edge is of any length greater than 1
        if circle_distance(e, g.graph['N']) > g.graph['K'] / 2:
            return 1.0 if np.random.random() < q else 0.0
        else:
            return 1.0 if np.random.random() < r else 0.0

    return knockout

def qr_knockout_lattice(q, r):
    '''
    Allows q of distant edges and r of close edges
    to be be traced (if they are adopted).
    For a 2D lattice.
    '''
    def knockout(g, e):
        # distance between u and v > size of original neighborhood / 2
        if square_distance(e, g.graph['N'], g.graph['M']) > 1:
            return 1.0 if np.random.random() < q else 0.0
        else:
            return 1.0 if np.random.random() < r else 0.0

    return knockout

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
    if type(params['A']) is float:
        nx.set_node_attributes(
            g,
            {x : np.random.random() < params['A'] for x in g.nodes()},
            name = 'adopter')
    elif callable(params['A']):
        #import pdb; pdb.set_trace()
        nx.set_node_attributes(g,
                               {
                                   i[0] : params['A'](g, i)
                                   for i
                                   in g.nodes(data = True)
                               },
                               name = 'adopter')
    else:
        print("No case found for Adoption rate.")
        pass

    # DEFAULT group assignment: if nodes are not in a group,
    # group them by whether they have adopted

    if 'group' not in g.nodes(0):
        nx.set_node_attributes(
            g,
            {x[0] : 1 if x[1]['adopter'] else 0 for x in g.nodes(data=True)},
            name = 'group'
        )

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
                'epi-state' : 'Infectious',
                'infected-at' : 0
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
        if np.random.random() <= edge[2][weight_attr]
        and not quarantined(g, edge)
    ]


## 2.a. Trace along active edge

## Can implement more flexible adoption logic later if need be...
def adoption(g, edge):
    return g.nodes[edge[0]]['adopter'] and g.nodes[edge[1]]['adopter']

def traced_contacts(g, active_edges, history, t):
    contact_history = dict()

    for edge in active_edges:
        if adoption(g, edge):
            if np.random.random() <= edge[2]['c']:
                if edge[0] not in contact_history:
                    contact_history[edge[0]] = set()

                if edge[1] not in contact_history:
                    contact_history[edge[1]] = set()

                contact_history[edge[0]].add(edge[1])
                contact_history[edge[1]].add(edge[0])

    history[t] = contact_history

    return contact_history


## 2.a. Infections along active edge

def infections(g, t, active_edges, beta_hat = .5, copy = True):
    if copy:
        g = g.copy()

    for edge in active_edges:
        if g.nodes[edge[0]]['epi-state'] == 'Infectious' \
        and g.nodes[edge[1]]['epi-state'] == 'Susceptible':
            if np.random.random() <= beta_hat:
                nx.set_node_attributes(
                    g,
                    { edge[1] :
                     {
                         'epi-state' : 'Exposed',
                         'exposed-at' : t
                     }
                    }
                )

                nx.set_edge_attributes(
                    g,
                    { (edge[0], edge[1]) :
                      {'route' : True}
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

                nx.set_edge_attributes(
                    g,
                    { (edge[0], edge[1]) :
                      {'route' : True}
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
                        'epi-state' : 'Infectious',
                        'infectious-at' : t
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
            if t_past in history:
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
                   t,
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

def simulation_process(g_live, params, i, time_limit = float("inf")):
    t = 0
    #g_live = g.copy()
    #initialize(g_live,params)
    history = {}

    s_count = []

    while len(get_infected(g_live)) > 0 and t < time_limit:
        if t != 0 and t % len(g_live.nodes()) / 100 == 0:
            print("Trial %d hits time step %d" % (i,t))

        s_count.append(len(susceptible(g_live)))

        g_live, history = loop(params, g_live, history, t)

        t = t + 1

    return data_from_result(
        t,
        params,
        g_live.copy(),
        history.copy(),
        s_count
    )

def initialize_graph(g, params):
    g_live = g.copy()

    initialize(g_live, params)

    return g_live

def simulate_sample(g, params, runs, time_limit = float("inf")):

    records = []

    tic = time.perf_counter()
    print("Initializing input graphs")

    clean_params = params.copy()

    # clear these out to support multiprocessing
    for k in clean_params:
        if callable(clean_params[k]):
            clean_params[k] = None

    inputs = zip(
        [initialize_graph(g, params) for i in range(runs)],
        [clean_params] * runs,
        range(runs)
    )

    toc = time.perf_counter()
    print(f"graphs prepared in {toc - tic}")

    pooling = True

    if pooling:
        pool = multiprocessing.Pool()
        records = pool.starmap(simulation_process, inputs)
        pool.close()
    else:
        records = [simulation_process(*i) for i in inputs]

    return records

def experiment(generator, base_params, conditions : dict, runs):
    """
    generator: takes keyword arguments and returns a graph and params dict
    conditions: a dictionary of dictionaries, with the keyword arguments
    runs: the number of runs per condition

    Returns:
    - dataframe!
    """
    results = {}

    for case in conditions:

        params = base_params.copy()
        params.update(conditions[case])

        g, params = generator(**params)

        print(f"Starting {case}")
        tic = time.perf_counter()
        results[case] = simulate_sample(
            g,
            params,
            runs
        )
        toc = time.perf_counter()
        print(f"Finished {case} in {toc - tic}")

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

    df = data_from_all_results(results)

    return df


### Data extraction

def route_adjacency_ratio(g):
    edges = g.edges(data=True)

    route_edges = [e for e in edges if 'route' in e[2]]

    if 'K' in g.graph:
        adjacent_edges = [e for e in route_edges
                          if circle_distance(
                                  e,
                                  g.graph['N']
                         ) <= (g.graph['K'] / 2)]
    else:
        adjacent_edges = [e for e in route_edges
                          if square_distance(
                                  e,
                                  g.graph['N'],
                                  g.graph['M']
                          ) <= 1]

    if len(route_edges) > 0:
        return float(len(adjacent_edges)) / len(route_edges)
    else:
        None



def traced_edges(g):
    edges = g.edges(data=True)

    te = 0
    te_d = 0

    for e in edges:
        if adoption(g, e) and g.edges[(e[0],e[1])]['c'] > 0.5:
            te += 1

            if 'K' in g.graph: # Watts-Strogatz case
                if circle_distance(e, g.graph['N']) > g.graph['K'] / 2:
                    te_d += 1
            else: # 2D lattice case
                if square_distance(e, g.graph['N'], g.graph['M']) > 1:
                    te_d += 1
    return te, te_d

def intervals(node_data):
    if 'exposed-at' not in node_data:
        exposed_interval = None
    elif 'infectious-at' in node_data: # normal exposure
        exposed_interval = node_data['infectious-at'] - node_data['exposed-at']
    else:
        exposed_interval = -1 # this is a bug.


    eff_infectious_interval = 0

    if 'infectious-at' in node_data:
        if 'quarantined-at' in node_data:
            # negative value means quarantined before becoming infectious!
            eii = node_data['quarantined-at'] - node_data['infectious-at']
        elif 'recovered-at' in node_data:
            eii = node_data['recovered-at'] - node_data['infectious-at']

        eff_infectious_interval = eii

    return exposed_interval, eff_infectious_interval

def effective_parameters(g):
    exposure_intervals = {}
    eff_infectious_intervals = {}

    # nodes for each group
    for x, d in g.nodes(data=True):
        group = d['group'] if 'group' in d else None

        e_interval, ei_interval = intervals(d)

        if e_interval is not None:
            if group not in exposure_intervals:
                exposure_intervals[group] = []

            exposure_intervals[group].append(e_interval)

        if ei_interval is not None:
            if group not in eff_infectious_intervals:
                eff_infectious_intervals[group] = []

            eff_infectious_intervals[group].append(ei_interval)

    average_exposure_intervals = {
        group : sum(exposure_intervals[group]) / len(exposure_intervals[group])
        for group
        in exposure_intervals
    }
    average_eff_infectious_intervals = {
         group : sum(eff_infectious_intervals[group]) / len(eff_infectious_intervals[group])
         for group
         in eff_infectious_intervals
    }

    return (average_exposure_intervals, average_eff_infectious_intervals)

def data_from_result(
        t,
        params,
        g,
        history,
        s_count
):
    te, te_d = traced_edges(g)

    aei, aeii = effective_parameters(g)

    group_0_adopters = len(
        [n for n in g.nodes(data=True)
         if n[1]['group'] == 0 and n[1]['adopter'] == 1])
    group_1_adopters = len(
        [n for n in g.nodes(data=True)
         if n[1]['group'] == 1 and n[1]['adopter'] == 1])
    group_0_size = len(
        [n for n in g.nodes(data=True) if n[1]['group'] == 0])
    group_1_size = len(
        [n for n in g.nodes(data=True) if n[1]['group'] == 1])

    if group_0_size > 0.0:
        group_0_adoption_rate = float(group_0_adopters) / group_0_size
    else:
        group_0_adoption_rate = float("nan")

    if group_1_size > 0:
        group_1_adoption_rate = float(group_1_adopters) / group_1_size
    else:
        group_1_adoption_rate = float("nan")

    return {
        'time' : t,
        **params,
        **g.graph,
        "s_final" : s_count[-1],
        "route_adjacent_ratio" : route_adjacency_ratio(g),
        "traced_edges" : te,
        "traced_edges_distant" : te_d,
        "group 0 adoption rate" : group_0_adoption_rate,
        "group 1 adoption rate" : group_1_adoption_rate,
        "avg. exp. interval - group 0" : aei[0] if 0 in aei else None,
        "avg. exp. interval - group 1" : aei[1] if 1 in aei else None,
        "avg. eff. inf. interval - group 0" : aeii[0] if 0 in aeii else None,
        "avg. eff. inf. interval - group 1" : aeii[1] if 1 in aeii else None
    }

def data_from_results(results, case):
    return [{**d,
             **{
                 "case" : case,
                 "infected_ratio" : (d['N'] - d['s_final']) / d['N']
             }}
            for d
            in results[case]]

def data_from_all_results(results):
    return pd.DataFrame([r for case in results for r in data_from_results(results, case)])


### Measuring output

def susceptible(g):
    return [n
            for n
            in g.nodes(data=True)
            if n[1]['epi-state'] == 'Susceptible']

def n_infected(g):
    return len(g.nodes()) - len(susceptible(g))

### THIS THIS BROKEN NOW
### This will need to be rewritten
def average_over_time(records, infected = False):
    N = len(records[0][2].nodes()) # Assumes constant N

    s_records = [r[4] for r in records]

    m = max([len(d) for d in s_records])

    s_plus = [d + [d[len(d)-1]] * (m - len(d)) for d in s_records]

    means = np.array([
        statistics.mean([d[i] for d in s_plus])
        for i
        in range(m)
    ])

    if infected:
        return N - means
    else:
        return means

### Graph Visualization

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

def edge_adopter(g, e):
    try:
        if len(e[2]['c']) > 0:
            print(e[2]['c'])
    except:
        pass

    e0a = g.nodes[e[0]]['adopter']
    e1a = g.nodes[e[1]]['adopter']

    return e0a and e1a

def edge_colors(g):
    edge_color = [
        ((1.0 if 'route' in e[2] and e[2]['route'] else 0 ),# else e[2]['w']),
         (e[2]['c'] * float(edge_adopter(g, e)) * 0.5),
          e[2]['c'] * int(edge_adopter(g, e)) * 0.5)
        for e
        in g.edges(data=True)
    ]

    return edge_color


def binned_heatmap(
        data,
        x = '',
        y = '',
        z = '',
        x_base = 10,
        y_base = 10,
        render = True
):
    '''
    Given some data, and column labels x, y, and z,
    and bases x_base and y_base ...

    ... create a heatmap of the average value of y
    over x and y binned by x_base and y_base respectively.
    '''
    d = data.copy()

    d['x_bin'] = d[x].apply(lambda x : x_base * round(float(x) / x_base))
    d['y_bin'] = d[y].apply(lambda y : y_base * round(float(y) / y_base))

    dg = d.groupby(['x_bin','y_bin'])[z].mean().reset_index()
    xyz = dg.pivot('y_bin','x_bin',z)

    if render:
        g = sns.heatmap(
            xyz
        )
    else:
        g = None

    return g, xyz, (d['x_bin'], d['y_bin'])
