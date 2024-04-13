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
    # for 
    graphnames = ['spa_500_{}'.format(graphidx) for graphidx in range(50)]
    GRAPHS = []
    for path in os.listdir("fair_influmax_code_release/networks"):
        g = pickle.load(open(f"fair_influmax_code_release/networks/{path}", 'rb'))
        g = nx.convert_node_labels_to_integers(g, label_attribute='pid')
        GRAPHS += [g]
    return GRAPHS
    


def find_pareto_fronts(wolves):
    objective_values = np.array([wolf.objective_values for wolf in wolves])
    domination_counts = np.sum(np.all(objective_values >= objective_values[:, np.newaxis], axis=2), axis=1)
    counter = 1
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
    # DEBUG = wolves[0]
    for i in range(ITERATIONS):
        time1 = time.time()
        a = 2 - i * (2/ITERATIONS)
        A = 2* a * np.random.rand(SEED_SIZE) - a
        C = 2* np.random.rand(len(g.nodes()))

        magnitude_A = np.linalg.norm(A)
        time9 = time.time()
        for wolf in wolves:
            wolf.ic_model()

        time2 = time.time()
        
        archive = find_pareto_fronts(wolves+archive)
        
        time3 = time.time()
        if len(archive)>3:
            leaders = random.sample(archive, 3)
        else:
            leaders = archive
        # print(len(archive), len(leaders[0].start), leaders[0].objective_values)    
        
        if len(leaders)==0:
            print("\n ARCHIVE \n")
            raise NotImplementedError
        now = time.time()
        for wolf in wolves:
            if wolf not in leaders:
                wolf.get_leader(leaders)
                wolf.get_next_start(magnitude_A)
        # print("-"*100)
        
        time4 = time.time()
        # print("Init: ", time9-time1)
        # print("IC: ", time2-time9)
        # print("Pareto: ", time3-time2)
        # print("Iterate: ", time4-time3)
        # print("Total: ", time4-time1)
        # print()            
    return archive


def simulate(GRAPHS, attribute, objectives, repetitions, pof):
    results =[]
    archives = []
    for _ in range(repetitions):
        for g in tqdm(GRAPHS):
            archive = setmogwo(g, attribute, objectives)
            archives += archive 
        gc.collect()
        
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

if __name__ == '__main__':
    main()
