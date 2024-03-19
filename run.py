import networkx as nx
import os
import pickle
from tqdm import tqdm
import numpy as np
import random
from collections import defaultdict
import copy
import time

PROPOGATION = 0.1
total_runs = 30
ITERATIONS = 100
SEED_SIZE = 25
POPULATION_SIZE = 500

from wolf import Wolf


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
    pareto_front = [copy.deepcopy(wolves[i]) for i, count in enumerate(domination_counts) if count == 1]
    return pareto_front

def setmogwo(g, attribute, objectives):
    wolves = [Wolf(g, attribute, objectives) for i in range(POPULATION_SIZE)]
    archive = []
    # DEBUG = wolves[0]
    for i in range(ITERATIONS):
        time1 = time.time()
        a = 2 - i * (2/ITERATIONS)
        A = 2* a * np.random.rand(len(g.nodes())) - a
        C = 2* np.random.rand(len(g.nodes()))

        magnitude_A = np.linalg.norm(A)
        time9 = time.time()
        for wolf in wolves:
            wolf.ic_model()
            if len(wolf.start)<20:
                wolf = Wolf(g, "age")
        time2 = time.time()
        
        archive = find_pareto_fronts(wolves+archive)
        
        time3 = time.time()
        if len(archive)>3:
            leaders = random.sample(archive, 3)
        else:
            leaders = archive
        # print(len(archive), len(leaders[0].start), leaders[0].objective_values)    
        
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


def simulate(GRAPHS, attribute, objectives, repetitions, pof, check=False):
    results =[]
    for _ in range(repetitions):
        for g in tqdm(GRAPHS):
            archive = setmogwo(g, attribute, objectives)
            for arch in archive:
                results += [[arch.influence_metric(), arch.maximin_fairness_metric(), arch.group_rationality_metric(), arch.group_activation_speed_metric()]]
            if check==True:
                break
            
    results = np.array(results)
    
    if pof:
    
        results2 =[]
        for _ in range(repetitions):
            for g in tqdm(GRAPHS):
                archive = setmogwo(g, attribute, {})
                for arch in archive:
                    results2 += [[arch.influence_metric(), arch.maximin_fairness_metric(), arch.group_rationality_metric(), arch.group_activation_speed_metric()]]
                if check==True:
                    break
                
        results2 = np.array(results2)
        return np.concatenate((np.average(results, axis=0),
                        np.array([sum(results[:,2]==0)/len(results)]), 
                        np.average(results2, axis=0)/(np.average(results, axis=0))))
    else: 
        np.append(np.average(results, axis=0),sum(results[:,2]==0)/len(results))
        
import argparse

def main():
    parser = argparse.ArgumentParser(description='Process attributes and metrics.')
    parser.add_argument('-a','--attribute', choices=["age", "gender", "ethnicity"], help='The attribute to process')
    parser.add_argument('-o','--objectives', nargs='+', choices={"maximin", "speed", "rationality"}, help='The metrics to use')    
    parser.add_argument('-r','--repetitions', type=int, help='Number of iterations (positive integer)')
    parser.add_argument('--pof', action='store_true', help='Set this flag to True')

    args = parser.parse_args()
    args.objectives = set(args.objectives)    
    GRAPHS = get_graphs()

    results = simulate(GRAPHS, args.attribute, args.objectives, args.repetitions, args.pof)
    algo_name = "SetMOGWO_I"
    for objective in args.objectives:
        algo_name += objective[0].upper()
    print(algo_name)

    final_results = {"name":algo_name, "attribute": args.attribute, 
                     "influence": results[0], "maximin": results[1],
                     "rationality": results[2], "speed": results[3],
                     "mean_rationality_violation": results[4]}
    print(final_results)
    
    print(results)
    return final_results
if __name__ == '__main__':
    main()
