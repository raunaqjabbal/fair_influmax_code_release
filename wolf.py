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
    def __init__(self, g, attribute, objectives, name=None):
        self.g = g
        self.g_len = len(self.g.nodes)
        self.start = set(np.random.choice(range(self.g_len), SEED_SIZE,replace=False))
        self.attribute = attribute
        self.v = set(range(self.g_len)) - self.start
        
        self.c = self.get_property(range(self.g_len))
        self.start_c = self.get_property(self.start)
        self.objectives = objectives
        
        self.name = name
        self.domination_count = 0
        self.dominated_wolves = set()
        self.objective_values = []
    #maximize
    def influence_metric(self):
        self.influence = len(self.next)
        return self.influence
    #maximize
    def maximin_fairness_metric(self):
        self.maximin_fairness = np.inf
        for kind, next_list in self.next_c.items():
            start_list = self.c[kind]    
            if self.maximin_fairness > len(next_list)/len(start_list):
                self.maximin_fairness = len(next_list)/len(start_list)
        return self.maximin_fairness
    #maximize
    def group_rationality_metric(self):
        self.group_rationality = self.influence
        for kind, next_list in self.next_c.items():
                                
            subgraph = self.g.subgraph(self.c[kind])
            
            activated_nodes = self.start_c[kind]
            newly_activated = self.start_c[kind]
            idx = 1 
            # self.group_activation_dict = defaultdict(list)
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
        return self.group_rationality
    
    #maximize
    def group_activation_speed_metric(self):
        self.group_activation_speed = np.inf
        if self.component[0]==0:
            self.group_activation_speed = 0
        else:
            for key, value in self.c.items():
                speed_key = np.dot(np.array(self.group_activation_dict[key]),self.component)/(self.component[0]*(len(value)-len(self.start_c[key])))                
                if speed_key < self.group_activation_speed:
                    self.group_activation_speed = speed_key
            
            if self.group_activation_speed == np.inf:
                self.group_activation_speed = 0
        return self.group_activation_speed
    def ic_model(self, g=None, start=None):
        if g==None:
            g = self.g
        if start == None:
            start = self.start.copy()
        activated_nodes = start.copy()
        newly_activated = start.copy()
        idx = 1 
        self.group_activation_dict = defaultdict(list)
        while newly_activated:
            next_round_activation = set()
            for node in newly_activated:
                neighbors = set(g.neighbors(node)) - activated_nodes
                for neighbor in neighbors:
                    if random.random() < PROPOGATION:
                        next_round_activation.add(neighbor)
            activated_nodes.update(next_round_activation)
            newly_activated = next_round_activation.copy()
            
            nij = self.get_property(newly_activated)
            
            for key,value in self.c.items():
                self.group_activation_dict[key] += [len(nij[key])] 
            idx += 1 
            
        self.component = np.array(range(idx - 2, -1, -1))
        
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
            if len(self.v)<self.g_len*0.8:
                self.v = set(range(self.g_len)) - self.start
            # if DEBUG==self:
            #     print("V:", len(self.v),"X:", len(self.start),"Leader:", len(self.leader))
            e_n = self.v - self.start.union(self.leader)
            e_o = self.start.intersection(self.leader) 
            d = len(self.start - self.leader)
            
            step = int(np.ceil((A-1)*d))
            # if DEBUG==self:
            #     print("e_n:", len(e_n),"e_o:", len(e_o),"step:", step)
            step = min(step, len(e_o), len(e_n))
            self.start = self.start - set(random.sample(list(e_o), step))
            # if DEBUG==self:
            #     print("Removing start: ", len(self.start))
            v_step = set(random.sample(list(e_n), step))
            self.start = self.start.union(v_step)
            # if DEBUG==self:
            #     print("Adding start: ", len(self.start))
            self.v = self.v - v_step 
            # if DEBUG==self:
            #     print("New V: ", len(self.v))
            #     print("\n\n")
                    
    def get_property(self,node_set):
        property_dict = defaultdict(list)
        for node in node_set:
            property_value = self.g.nodes[node][self.attribute]
            if property_value not in property_dict:
                property_dict[property_value] = []
            property_dict[property_value].append(node)

        for key, value in property_dict.items():
            property_dict[key] = set(value)
        return property_dict
    
    def get_leader(self, wolves):
        min_difference = float('inf')
        self.leader = set()
        for X in wolves:
            difference = len(self.start - X.start)
            if difference < min_difference:
                min_difference = difference
                self.leader = X.start.copy()
        # self.leader = set(random.sample(list(self.leader), int((len(self.leader)*0.6))))

