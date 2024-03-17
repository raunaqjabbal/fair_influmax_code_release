from joblib import Parallel, delayed


# def find_pareto_fronts(wolves):
#     pareto_fronts = []
#     for wolf in wolves:
#         wolf.domination_count = 0
#         wolf.dominated_wolves = set()
    
#     for i, wolf1 in enumerate(wolves):
#         for j, wolf2 in enumerate(wolves):
#             if i != j:
#                 if np.all(wolf1.objective_values>wolf2.objective_values):
#                     wolf2.dominated_wolves.add(wolf1)
#                 elif np.all(wolf1.objective_values<wolf2.objective_values):
#                     wolf1.domination_count += 1
    
#     front = [wolf for wolf in wolves if wolf.domination_count == 0]
#     pareto_fronts.append(front)

#     # current_front = 0
#     # while len(pareto_fronts[current_front]) > 0:
#     #     next_front = []
#     #     for wolf in pareto_fronts[current_front]:
#     #         for dominated_wolf in wolf.dominated_wolves:
#     #             dominated_wolf.domination_count -= 1
#     #             if dominated_wolf.domination_count == 0:
#     #                 next_front.append(dominated_wolf)
#     #     current_front += 1
#     #     pareto_fronts.append(next_front)

#     return pareto_fronts


# def find_pareto_fronts(wolves):
#     num_wolves = len(wolves)
#     objective_values = np.array([wolf.objective_values for wolf in wolves])
#     front = []
#     for i in range(num_wolves):
#         # domination_counts = np.all(objective_values < objective_values[i], axis=1)
#         wolves[i].domination_count = sum(np.all(objective_values > objective_values[i], axis=1))
        
#         if wolves[i].domination_count==0:
#             front += [wolves[i]]    

#         # dominated_wolves_idx = np.where(domination_counts)        
#         # if dominated_wolves_idx != []:
#         #     for j in dominated_wolves_idx
#         #         print(type(wolves[i].dominated_wolves))  #.add(wolves[j])
#         #         print(wolves[j])
        
#     return front



def find_pareto_fronts(wolves):
    objective_values = np.array([wolf.objective_values for wolf in wolves])
    domination_counts = np.sum(np.all(objective_values > objective_values[:, np.newaxis], axis=2), axis=1)
    pareto_front = [wolves[i] for i, count in enumerate(domination_counts) if count == 0]
    return pareto_front


# def select_best_wolves(pareto_fronts, num):
#     selected_wolves = []
#     for front in pareto_fronts:
#         if len(front) <= num:
#             selected_wolves.extend(front)
#             num = num - len(front)
#         else:
#             selected_wolves.extend(random.sample(front, num))
    
#     return selected_wolves


# if step == int(np.ceil((A-1)*d)) and god!="Ceil":
#     print("Ceil: ",int(np.ceil((A-1)*d)))
#     god = "Ceil"
# elif step == len(e_o) and god!="e_o":
#     print("e_o: ", len(e_o))
#     god = "e_o"
# elif step == len(e_n) and god!="e_n":
#     print("e_n: ", len(e_n))
#     god = "e_n"
