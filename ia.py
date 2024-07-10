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
    actions = [(unit.x, unit.y)]
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            new_x, new_y = unit.x + dx, unit.y + dy
            if 0 <= new_x < size and 0 <= new_y < size and not any(u.x == new_x and u.y == new_y and u.color == (255, 0, 0) for u in units):
                actions.append((new_x, new_y))
    return actions

def initialize_q_table(state, units, size):
    key = state_to_key(state)
    if key not in q_table:
        q_table[key] = {}
        for unit in state['units']:
            if unit.color == (255, 0, 0): # ENEMY_COLOR
                for action in get_possible_actions(unit, units, size):
                    if action not in q_table[key]:
                        q_table[key][action] = 0

def choose_action(state, unit, units, size):
    key = state_to_key(state)
    initialize_q_table(state, units, size)

    possible_actions = get_possible_actions(unit, units, size)
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

def get_reward(unit, objectives, units):
    reward = 0
    for obj in objectives:
        if unit.x == obj['x'] and unit.y == obj['y']:
            reward += 5 if obj['type'] == 'MAJOR' else 2

    for target in units:
        if target.color != unit.color and abs(unit.x - target.x) <= 1 and abs(unit.y - target.y) <= 1:
            reward += 10

    return reward

def perform_action(unit, action, units, objectives, size):
    """Effectue une action choisie par l'IA."""
    target_x, target_y = action
    target_unit = next((u for u in units if u.x == target_x and u.y == target_y and u.color != unit.color), None)

    if target_unit:
        unit.attack(target_unit, units, objectives)
    else:
        unit.move(target_x, target_y, units)

def enemy_turn(units, objectives, size):
    state = {'units': units, 'objectives': objectives}
    for unit in units:
        if unit.color == (255, 0, 0):  # ENEMY_COLOR
            action = choose_action(state, unit, units, size)
            next_x, next_y = action

            unit.x, unit.y = next_x, next_y

            reward = get_reward(unit, objectives, units)
            next_state = {'units': units, 'objectives': objectives}
            update_q_table(state, action, reward, next_state, units, size)


def player_turn(units, objectives, size):
    state = {'units': units, 'objectives': objectives}
    for unit in units:
        if unit.color == (0, 0, 255):  # PLAYER_COLOR
            action = choose_action(state, unit, units, size)
            next_x, next_y = action

            unit.x, unit.y = next_x, next_y

            reward = get_reward(unit, objectives, units)
            next_state = {'units': units, 'objectives': objectives}
            update_q_table(state, action, reward, next_state, units, size)

def save_q_table(filename='q_table.pkl'):
    with open(filename, 'wb') as f:
        pickle.dump(q_table, f)

def load_q_table(filename='q_table.pkl'):
    global q_table
    with open(filename, 'rb') as f:
        q_table = pickle.load(f)