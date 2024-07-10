import random
import numpy as np
import pickle

gamma = 0.9
alpha = 0.1
epsilon = 0.1
q_table = {}

def state_to_key(state):
    return tuple((unit.x, unit.y, unit.color) for unit in state['units']) + tuple((obj['x'], obj['y'], obj['type']) for obj in state['objectives'])

def get_possible_actions(unit, units, size):
    actions = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            new_x, new_y = unit.x + dx, unit.y + dy
            if 0 <= new_x < size and 0 <= new_y < size and not any(u.x == new_x and u.y == new_y and u.color == unit.color for u in units):
                actions.append((new_x, new_y))
    return actions

def initialize_q_table(state, units, size):
    key = state_to_key(state)
    if key not in q_table:
        q_table[key] = {}
        for unit in state['units']:
            if unit.color in [(255, 0, 0), (0, 0, 255)]:  # ENEMY_COLOR or PLAYER_COLOR
                for action in get_possible_actions(unit, units, size):
                    if action not in q_table[key]:
                        q_table[key][action] = 0

def choose_action(state, unit, units, size, epsilon=0.1):
    key = state_to_key(state)
    initialize_q_table(state, units, size)

    possible_actions = get_possible_actions(unit, units, size)
    if not possible_actions:
        return (unit.x, unit.y)  # Si aucune action possible, rester sur place

    if random.uniform(0, 1) < epsilon:
        return random.choice(possible_actions)
    else:
        action_values = {action: q_table[key].get(action, 0) for action in possible_actions}
        best_action = max(action_values, key=action_values.get)
        return best_action

def update_q_table(state, action, reward, next_state, units, size):
    key = state_to_key(state)
    next_key = state_to_key(next_state)

    initialize_q_table(state, units, size)
    initialize_q_table(next_state, units, size)

    best_next_action = max(q_table[next_key], key=q_table[next_key].get, default=(0, 0))
    td_target = reward + gamma * q_table[next_key].get(best_next_action, 0)
    td_error = td_target - q_table[key].get(action, 0)
    q_table[key][action] = q_table[key].get(action, 0) + alpha * td_error

def get_reward(unit, objectives, units, size):
    reward = 0
    for obj in objectives:
        if unit.x == obj['x'] and unit.y == obj['y']:
            reward += 3 if obj['type'] == 'MAJOR' else 1

    for target in units:
        if target.color != unit.color and abs(unit.x - target.x) <= 1 and abs(unit.y - target.y) <= 1:
            reward += 10

    # Pénalité pour les coins
    if (unit.x == 0 and unit.y == 0) or (unit.x == 0 and unit.y == size - 1) or (unit.x == size - 1 and unit.y == 0) or (unit.x == size - 1 and unit.y == size - 1):
        reward -= 5

    return reward

def perform_action(unit, action, units, objectives, size):
    """Effectue une action choisie par l'IA."""
    target_x, target_y = action
    target_unit = next((u for u in units if u.x == target_x and u.y == target_y and u.color != unit.color), None)

    if target_unit:
        unit.attack(target_unit, units, objectives)
    else:
        unit.move(target_x, target_y, units)

def strategic_choose_action(state, unit, units, size, objectives):
    key = state_to_key(state)
    initialize_q_table(state, units, size)

    possible_actions = get_possible_actions(unit, units, size)
    if not possible_actions:
        return (unit.x, unit.y)  # Si aucune action possible, rester sur place

    action_values = {action: q_table[key].get(action, 0) for action in possible_actions}
    
    # Prioritize objectives
    objective_actions = [action for action in possible_actions if any(obj['x'] == action[0] and obj['y'] == action[1] for obj in objectives)]
    if objective_actions:
        return random.choice(objective_actions)  # Choisir aléatoirement parmi les actions d'objectif
    
    # Reinforce if threatened
    for action in possible_actions:
        target_unit = next((u for u in units if u.x == action[0] and u.y == action[1] and u.color != unit.color), None)
        if target_unit:
            return action  # Attack
    
    # Avoid corners
    non_corner_actions = [action for action in possible_actions if (action[0] != 0 and action[0] != size - 1 and action[1] != 0 and action[1] != size - 1)]
    if non_corner_actions:
        return random.choice(non_corner_actions)  # Choisir aléatoirement parmi les actions non-corners
    
    # Default to best Q-value action
    best_action = max(action_values, key=action_values.get)
    return best_action

def enemy_turn(units, objectives, size):
    state = {'units': units, 'objectives': objectives}
    all_units_moved = True
    objective_units = 0
    for unit in units:
        if unit.color == (255, 0, 0):  # ENEMY_COLOR
            initial_position = (unit.x, unit.y)
            action = strategic_choose_action(state, unit, units, size, objectives)
            perform_action(unit, action, units, objectives, size)
            next_state = {'units': units, 'objectives': objectives}
            reward = get_reward(unit, objectives, units, size)
            if (unit.x, unit.y) == initial_position:
                reward -= 1  # Pénalité si l'unité n'a pas bougé
                all_units_moved = False
            update_q_table(state, action, reward, next_state, units, size)
            if any(obj['x'] == unit.x and obj['y'] == unit.y for obj in objectives):
                objective_units += 1

    # Si moins de deux unités ennemies sont sur les objectifs, assigner deux unités aux objectifs
    if objective_units < 2:
        assigned_units = 0
        for unit in units:
            if unit.color == (255, 0, 0):  # ENEMY_COLOR
                if assigned_units >= 2:
                    break
                for obj in objectives:
                    if not any(u.x == obj['x'] and u.y == obj['y'] for u in units):
                        action = (obj['x'], obj['y'])
                        perform_action(unit, action, units, objectives, size)
                        next_state = {'units': units, 'objectives': objectives}
                        reward = get_reward(unit, objectives, units, size)
                        update_q_table(state, action, reward, next_state, units, size)
                        assigned_units += 1
                        break

    if not all_units_moved:
        for unit in units:
            if unit.color == (255, 0, 0):
                state = {'units': units, 'objectives': objectives}
                reward = -5  # Pénalité globale si au moins une unité ne bouge pas
                next_state = {'units': units, 'objectives': objectives}
                update_q_table(state, (unit.x, unit.y), reward, next_state, units, size)

def player_turn(units, objectives, size):
    state = {'units': units, 'objectives': objectives}
    all_units_moved = True
    objective_units = 0
    for unit in units:
        if unit.color == (0, 0, 255):  # PLAYER_COLOR
            initial_position = (unit.x, unit.y)
            action = strategic_choose_action(state, unit, units, size, objectives)
            perform_action(unit, action, units, objectives, size)
            next_state = {'units': units, 'objectives': objectives}
            reward = get_reward(unit, objectives, units, size)
            if (unit.x, unit.y) == initial_position:
                reward -= 1  # Pénalité si l'unité n'a pas bougé
                all_units_moved = False
            update_q_table(state, action, reward, next_state, units, size)
            if any(obj['x'] == unit.x and obj['y'] == unit.y for obj in objectives):
                objective_units += 1

    # Si moins de deux unités alliées sont sur les objectifs, assigner deux unités aux objectifs
    if objective_units < 2:
        assigned_units = 0
        for unit in units:
            if unit.color == (0, 0, 255):  # PLAYER_COLOR
                if assigned_units >= 2:
                    break
                for obj in objectives:
                    if not any(u.x == obj['x'] and u.y == obj['y'] for u in units):
                        action = (obj['x'], obj['y'])
                        perform_action(unit, action, units, objectives, size)
                        next_state = {'units': units, 'objectives': objectives}
                        reward = get_reward(unit, objectives, units, size)
                        update_q_table(state, action, reward, next_state, units, size)
                        assigned_units += 1
                        break

    if not all_units_moved:
        for unit in units:
            if unit.color == (0, 0, 255):
                state = {'units': units, 'objectives': objectives}
                reward = -5  # Pénalité globale si au moins une unité ne bouge pas
                next_state = {'units': units, 'objectives': objectives}
                update_q_table(state, (unit.x, unit.y), reward, next_state, units, size)

def save_q_table(filename='q_table.pkl'):
    with open(filename, 'wb') as f:
        pickle.dump(q_table, f)

def load_q_table(filename='q_table.pkl'):
    global q_table
    with open(filename, 'rb') as f:
        q_table = pickle.load(f)
