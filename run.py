import networkx as nx
import os
import pickle
from tqdm import tqdm
import numpy as np
import random
from collections import defaultdict
import copy
import time
import json

PROPOGATION = 0.1
total_runs = 30
ITERATIONS = 10
SEED_SIZE = 25
POPULATION_SIZE = 500

from wolf import Wolf
import gc

def get_graphs():
    GRAPHS = []
    for path in os.listdir("fair_influmax_code_release/networks"):
        g = pickle.load(open(f"fair_influmax_code_release/networks/{path}", 'rb'))
        g = nx.convert_node_labels_to_integers(g, label_attribute='pid')
        GRAPHS += [g]
    return GRAPHS

def find_pareto_fronts(wolves):
    objective_values = np.array([wolf.objective_values for wolf in wolves])
    domination_counts = np.sum(np.any(objective_values > objective_values[:, np.newaxis], axis=2), axis=1)
    counter = 0
    while True:
        pareto_front = [copy.deepcopy(wolves[i]) for i, count in enumerate(domination_counts) if count == counter]
        if pareto_front:
            break
        else:
            counter+=1
    return pareto_front

def setmogwo(g, attribute, objectives):
    wolves = [Wolf(g, attribute, objectives) for i in range(POPULATION_SIZE)]
    archive = []
    for i in range(ITERATIONS):
        a = 2 - i * (2/ITERATIONS)
        A = 2* a * np.random.rand(SEED_SIZE) - a
        C = 2* np.random.rand(SEED_SIZE)

        magnitude_A = np.linalg.norm(A)
        for wolf in wolves:
            wolf.ic_model()
        archive = find_pareto_fronts(wolves+archive)
        if len(archive)>3:
            leaders = random.sample(archive, 3)
        else:
            leaders = archive
        
        if len(leaders)==0:
            raise NotImplementedError
        new_wolves = []
        for wolf in wolves:
            # if wolf not in leaders:
            pups_start = wolf.get_next_start(magnitude_A,leaders)
            for pup_start in pups_start:
                pup = Wolf(g, attribute, objectives)
                pup.start = pup_start
                new_wolves += [pup]
        wolves = new_wolves
                
    return archive


def simulate(GRAPHS, attribute, objectives, repetitions, pof):
    results =[]
    archives = []
    for _ in pit(range(repetitions), color="red"):
        for g in pit(GRAPHS, color="blue"):
            archive = setmogwo(g, attribute, objectives)
            archives += archive 
        # gc.collect()
        
    archives = find_pareto_fronts(archives)
    for arch in archives:
        results += [[arch.influence_metric(), arch.maximin_fairness_metric(), arch.group_rationality_metric(), arch.group_activation_speed_metric()]]
            
    results = np.array(results)
    return np.append(np.average(results, axis=0),sum(results[:,2]==0)/len(results))
        
import argparse

def main():
    parser = argparse.ArgumentParser(description='Process attributes and metrics.')
    parser.add_argument('-a','--attribute', choices=["age", "gender", "ethnicity"], help='The attribute to process')
    parser.add_argument('-o','--objectives', nargs='+', choices={"maximin", "speed", "rationality"}, help='The metrics to use')    
    parser.add_argument('-r','--repetitions', type=int, help='Number of iterations (positive integer)')
    parser.add_argument('--pof', action='store_true', help='Set this flag to True')

    algo_name = "SetMOGWO_I"
    args = parser.parse_args()
    if args.objectives:
        args.objectives = set(args.objectives)    
        for objective in args.objectives:
            algo_name += objective[0].upper()
    else:
        args.objectives = set()
    GRAPHS = get_graphs()
    
    FILENAME = f"{algo_name}_{args.attribute}.json"
    print(FILENAME)
    results = simulate(GRAPHS, args.attribute, args.objectives, args.repetitions, args.pof)
    if args.pof:
        final_results = {"algorithm":algo_name, "attribute": args.attribute, 
                        "influence": results[0], "maximin": results[1],
                        "rationality": results[2], "speed": results[3],
                        "mean_rationality_violation": results[4:]}
    else:
        final_results = {"algorithm":algo_name, "attribute": args.attribute, 
                        "influence": results[0], "maximin": results[1],
                        "rationality": results[2], "speed": results[3],
                        "mean_rationality_violation": results[4]}    
    print(final_results)
    
    with open(os.path.join("data", FILENAME), 'w') as json_file:
        json.dump(final_results, json_file)
    
    return final_results


def pit(it, *pargs, **nargs):
    import enlighten
    global __pit_man__
    try:
        __pit_man__
    except NameError:
        __pit_man__ = enlighten.get_manager()
    man = __pit_man__
    it_len = len(it)
    ctr = None
    ctr = None
    for i, e in enumerate(it):
        if i == 0:
            ctr = man.counter(*pargs, **{**dict(leave = False, total = it_len), **nargs})
        yield e
        ctr.update()
    if ctr is not None:
        ctr.close()
        
if __name__ == '__main__':
    main()
