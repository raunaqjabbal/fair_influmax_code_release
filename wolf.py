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

class Wolf:
    def __init__(self, g, attribute, objectives):
        self.g = g
        self.g_len = len(self.g.nodes)
        self.start = set(np.random.choice(range(self.g_len), SEED_SIZE,replace=False))    
        self.attribute = attribute
        self.v = set(range(self.g_len)) - self.start
        
        self.c = self.get_property(range(self.g_len))
        self.start_c = self.get_property(self.start)
        self.objectives = objectives
        
        self.subgraph = {key: self.g.subgraph(self.c[key]) for key,_ in self.c.items()}
        self.objective_values = []

    def influence_metric(self):
        self.influence = len(self.next)
        return self.influence

    def maximin_fairness_metric(self):
        self.maximin_fairness = 2
        for kind, start_list in self.c.items():
            ratio = self.next_c[kind]/len(start_list)
            if self.maximin_fairness > ratio:
                self.maximin_fairness = ratio
        return self.maximin_fairness

    def group_rationality_metric(self):
        self.group_rationality = self.influence
        for kind, start_list in self.c.items():                                
            next_list = self.next_c[kind]
            subgraph = self.subgraph[kind]
            init = int(np.ceil(len(self.c[kind])*SEED_SIZE/self.g_len))
            init_nodes = set(random.sample(list(start_list), init))
            activated_nodes = init_nodes
            newly_activated = init_nodes
            while newly_activated:
                next_round_activation = set()
                for node in newly_activated:
                    neighbors = set(subgraph.neighbors(node)) - activated_nodes
                    for neighbor in neighbors:
                        if random.random() < PROPOGATION:
                            next_round_activation.add(neighbor)
                activated_nodes.update(next_round_activation)
                newly_activated = next_round_activation
                
            if len(next_list) <= len(activated_nodes):
                self.group_rationality = 0
                break
        return self.group_rationality
    
    #maximize
    def group_activation_speed_metric(self):
        self.group_activation_speed = np.inf
        
        for key, value in self.c.items():
            speed_key = np.dot(np.array(self.group_activation_dict[key]),self.component)/(self.component[0]*len(value - self.start_c[key].intersection(value)) )                
            if speed_key < self.group_activation_speed:
                self.group_activation_speed = speed_key
        
        if self.group_activation_speed == np.inf:
            raise NotImplementedError
            # self.group_activation_speed = 0
        return self.group_activation_speed
    
    def ic_model(self, g=None, start=None):
        if g==None:
            g = self.g
        if start == None:
            start = self.start.copy()
        activated_nodes = start.copy()
        newly_activated = start.copy()
        idx = 0
        self.group_activation_dict = defaultdict(list)
        while newly_activated:
            next_round_activation = set()
            for node in newly_activated:
                neighbors = (set(g.neighbors(node)) - activated_nodes) - newly_activated
                for neighbor in neighbors:
                    if random.random() < PROPOGATION:
                        next_round_activation.add(neighbor)
            newly_activated = next_round_activation.copy()
            activated_nodes.update(newly_activated)
            
            nij = self.get_property(newly_activated)
            
            for key,value in self.c.items():
                self.group_activation_dict[key] += [len(nij[key])] 
            idx += 1 
            
        self.component = np.array(range(idx , 0, -1))
        
        self.next = activated_nodes
        self.next_c = self.get_property(self.next)
        

        self.objective_values = [self.influence_metric()]
        if "maximin" in self.objectives:
            self.objective_values+=[self.maximin_fairness_metric()]
        if "speed" in self.objectives:
            self.objective_values+=[self.group_activation_speed_metric()]
        if "rationality" in self.objectives:
            self.objective_values+=[self.group_rationality_metric()]
        
        self.objective_values = np.round(self.objective_values,4)

        
    def get_next_start(self,A):
        global DEBUG
        if A<1:
            e_n = self.leader - self.start
            e_o = self.start - self.leader
            d = len(e_o)
            step = int(np.ceil((1-A)*d))
            step = min(step, len(e_o), len(e_n))
            self.start = self.start - set(random.sample(list(e_o), step))
            self.start = self.start.union(set(random.sample(list(e_n), step)))
            
        else:
            if len(self.v)<self.g_len*0.25:
                self.v = set(range(self.g_len)) - self.start
            e_n = self.v - self.start.union(self.leader)
            e_o = self.start.intersection(self.leader) 
            d = len(self.start - self.leader)
            
            step = int(np.ceil((A-1)*d))
            step = min(step, len(e_o), len(e_n))
            
            self.start = self.start - set(random.sample(list(e_o), step))
            v_step = set(random.sample(list(e_n), step))
            self.start = self.start.union(v_step)
            self.v = self.v - v_step 
            
                    
    def get_property(self,node_set):
        property_dict = defaultdict(set)
        for node in node_set:
            property_dict[self.g.nodes[node][self.attribute]].add(node)
        return property_dict
    
    def get_leader(self, leaders):
        min_difference = SEED_SIZE+1
        self.leader = set()
        random.shuffle(leaders)

        if len(leaders)>0:
            for X in leaders:
                difference = len(self.start - X.start)
                if difference < min_difference:
                    min_difference = difference
                    self.leader = set(X.start)
        else:
            raise NotImplementedError
            # self.leader =  set(np.random.choice(range(self.g_len), SEED_SIZE,replace=False))
        self.leader = set(np.array(list(self.leader))[np.random.rand(SEED_SIZE) < np.random.rand(SEED_SIZE)])
