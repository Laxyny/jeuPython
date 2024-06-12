import random
import numpy as np

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
            if 0 <= new_x < size and 0 <= new_y < size and not any(u.x == new_x and u.y == new_y and u.color == unit.color for u in units):
                actions.append((new_x, new_y))
    return actions

def initialize_q_table(state, units, size):
    key = state_to_key(state)
    if key not in q_table:
        q_table[key] = {}
        for unit in state['units']:
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
        return max(action_values, key=action_values.get)

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
            reward += 2 if obj['type'] == 'MAJOR' else 1

    for target in units:
        if target.color != unit.color and abs(unit.x - target.x) <= 1 and abs(unit.y - target.y) <= 1:
            reward += 3

    reward += check_for_capture(unit, units)

    return reward

def check_for_capture(unit, units):
    reward = 0
    for dx in [-1, 1]:
        if any(u.x == unit.x + dx and u.y == unit.y and u.color != unit.color for u in units):
            if any(u.x == unit.x - dx and u.y == unit.y and u.color == unit.color for u in units):
                reward += 5 

    for dy in [-1, 1]:
        if any(u.x == unit.x and u.y == unit.y + dy and u.color != unit.color for u in units):
            if any(u.x == unit.x and u.y == unit.y - dy and u.color == unit.color for u in units):
                reward += 5

    return reward

def enemy_turn(units, objectives, size):
    state = {'units': units, 'objectives': objectives}
    for unit in units:
        if unit.color == (255, 0, 0):
            action = choose_action(state, unit, units, size)
            next_x, next_y = action

            for target in units:
                if target.x == next_x and target.y == next_y:
                    if target.color == unit.color:
                        break
                    else:
                        for ally in units:
                            if ally.color == unit.color and ally.x == unit.x and ally.y == unit.y:
                                target.x, target.y = target.x + (target.x - unit.x), target.y + (target.y - unit.y)
                                unit.x, unit.y = next_x, next_y
                                break
                        else:
                            units.remove(target)
                            unit.x, unit.y = next_x, next_y
                        break
            else:
                unit.x, unit.y = next_x, next_y

            reward = get_reward(unit, objectives, units)
            next_state = {'units': units, 'objectives': objectives}
            update_q_table(state, action, reward, next_state, units, size)


def player_turn(units, objectives, size):
    state = {'units': units, 'objectives': objectives}
    for unit in units:
        if unit.color == (0, 0, 255):
            action = choose_action(state, unit, units, size)
            next_x, next_y = action

            for target in units:
                if target.x == next_x and target.y == next_y:
                    if target.color == unit.color:
                        break
                    else:
                        for ally in units:
                            if ally.color == unit.color and ally.x == unit.x and ally.y == unit.y:
                                target.x, target.y = target.x + (target.x - unit.x), target.y + (target.y - unit.y)
                                unit.x, unit.y = next_x, next_y
                                break
                        else:
                            units.remove(target)
                            unit.x, unit.y = next_x, next_y
                        break
            else:
                unit.x, unit.y = next_x, next_y

            reward = get_reward(unit, objectives, units)
            next_state = {'units': units, 'objectives': objectives}
            update_q_table(state, action, reward, next_state, units, size)
