import ex3
import time
import inputs
import random

CODES = {"passage": 10, "hero 1": 11, "hero 2": 12, "hero 3": 13, "hero 4": 14,
         "wall": 20, "pit": 30, "monster": 60, "gold": 70, "target": 75}
INVERSE_CODES = dict([(j, i) for i, j in CODES.items()])
ACTION_TIMEOUT = 5
CONSTRUCTOR_TIMEOUT = 60
RESET_PENALTY = 15
GOAL_POINTS = 10
PROBABILITY_OF_SUCCESS = 0.7
PROBABILITY_OF_SIDESTEP = 0.1


class StochasticChecker:
    def __init__(self, turn_limit, input):
        self.initial_state = wrap_with_walls(input)
        self.x_dimension = len(self.initial_state)
        self.y_dimension = len(self.initial_state[0])
        self.current_state = state_to_dict(self.initial_state)
        self.turn_limit = turn_limit
        self.points = 0
        self.gold_flag = False
        print(f"Maximal amount of turns is {self.turn_limit}!")

    def true_state_to_controller_input(self):
        state_to_return = []
        for i in range(len(self.initial_state)):
            row = []
            for j in range(len(self.initial_state[0])):
                row.append(self.current_state[(i, j)])
            state_to_return.append(row)
        state_to_return = [row[1:-1] for row in state_to_return[1:-1]]
        return self.turn_limit, state_to_return


    def check_controller(self):
        constructor_start = time.time()
        turns_limit, map = self.true_state_to_controller_input()
        controller = ex3.WumpusStochasticController(turns_limit, map)
        constructor_finish = time.time()
        if constructor_finish - constructor_start > CONSTRUCTOR_TIMEOUT:
            return f"Timeout on constructor! Took {constructor_finish - constructor_start} seconds," \
                   f" should take no more than {CONSTRUCTOR_TIMEOUT}"
        for turn in range(self.turn_limit):
            turns_limit, state_to_controller = self.true_state_to_controller_input()
            turns_limit -= turn
            start = time.time()
            action = controller.get_next_action(turns_limit, state_to_controller)
            finish = time.time()
            if finish-start > ACTION_TIMEOUT:
                return f"Timeout on action! Took {finish - start} seconds, should take no more than {ACTION_TIMEOUT}"
            if not self.is_action_legal(action):
                return f"Action {action} is illegal!"
            self.change_state_after_action(action)
            self.score_points(action)
        return f"accumulated {self.points} points!"

    def is_action_legal(self, action):
        if action == "reset":
            return True
        if len(action) != 3:
            return False
        name_of_action, hero, direction = action[0], action[1], action[2]
        if not (name_of_action == "shoot" or name_of_action == "move"):
            return False
        if hero not in self.current_state.values():
            return False
        if direction not in ("U", "D", "L", "R"):
            return False
        return True

    def change_state_after_action(self, action):
        if action == "reset":
            self.current_state = state_to_dict(self.initial_state)
            return
        if action[0] == "move":
            self.change_state_after_moving(action)
        else:
            self.change_state_after_shooting(action)


    def change_state_after_moving(self, action):
        hero, direction = action[1], action[2]
        current_tile = None
        for i, j in self.current_state.items():
            if j == hero:
                current_tile = i

        if direction == "U":
            next_tile = (current_tile[0] - 1, current_tile[1])
        elif direction == "D":
            next_tile = (current_tile[0] + 1, current_tile[1])
        elif direction == "R":
            next_tile = (current_tile[0], current_tile[1] + 1)
        elif direction == "L":
            next_tile = (current_tile[0], current_tile[1] - 1)
        assert next_tile

        destination_object = INVERSE_CODES[self.current_state[next_tile]]
        if destination_object == "wall" or "hero" in destination_object:
            return
        next_tile = self.randomize_move(next_tile, direction)
        destination_object = INVERSE_CODES[self.current_state[next_tile]]

        self.current_state[current_tile] = CODES["passage"]
        if destination_object == "passage":
            self.current_state[next_tile] = hero
            self.monster_correction(next_tile, False)
        elif destination_object == "gold":
            self.current_state[next_tile] = hero
            self.gold_flag = True
            self.monster_correction(next_tile, True)
        return

    def randomize_move(self, next_tile, direction):
        if direction == "U":
            sidestep_tiles = [(next_tile[0] - 1, next_tile[1]),
                              (next_tile[0], next_tile[1] - 1),
                              (next_tile[0], next_tile[1] + 1)]
        elif direction == "D":
            sidestep_tiles = [(next_tile[0] + 1, next_tile[1]),
                              (next_tile[0], next_tile[1] - 1),
                              (next_tile[0], next_tile[1] + 1)]
        elif direction == "R":
            sidestep_tiles = [(next_tile[0] - 1, next_tile[1]),
                              (next_tile[0] + 1, next_tile[1]),
                              (next_tile[0], next_tile[1] + 1)]
        elif direction == "L":
            sidestep_tiles = [(next_tile[0] - 1, next_tile[1]),
                              (next_tile[0] + 1, next_tile[1]),
                              (next_tile[0], next_tile[1] - 1)]
        assert sidestep_tiles
        population = [next_tile] + sidestep_tiles
        probabilities = [PROBABILITY_OF_SUCCESS, PROBABILITY_OF_SIDESTEP, PROBABILITY_OF_SIDESTEP, PROBABILITY_OF_SIDESTEP]
        assert len(population) == 4 and len(probabilities) == 4
        chosen_tile = tuple(random.choices(population, weights=probabilities))[0]
        if INVERSE_CODES[self.current_state[chosen_tile]] not in ["passage", "gold", "pit", "monster"]:
            chosen_tile = next_tile
        return chosen_tile

    def monster_correction(self, tile, gold):
        relevant_locations = (
            (tile[0] - 1, tile[1]),
            (tile[0] + 1, tile[1]),
            (tile[0], tile[1] - 1),
            (tile[0], tile[1] + 1)
        )

        for location in relevant_locations:
            if self.current_state[location] == CODES["monster"]:
                self.current_state[location] = CODES["passage"]
                if gold:
                    self.current_state[tile] = CODES["gold"]
                else:
                    self.current_state[tile] = CODES["passage"]


    def change_state_after_shooting(self, action):
        hero, direction = action[1], action[2]
        current_tile = None
        for i, j in self.current_state.items():
            if j == hero:
                current_tile = i
        next_tile = current_tile
        while True:
            if direction == "U":
                next_tile = (next_tile[0] - 1, next_tile[1])
            elif direction == "D":
                next_tile = (next_tile[0] + 1, next_tile[1])
            elif direction == "R":
                next_tile = (next_tile[0], next_tile[1] + 1)
            elif direction == "L":
                next_tile = (next_tile[0], next_tile[1] - 1)
            if (self.current_state[next_tile] == CODES["passage"] or self.current_state[next_tile] == CODES[
                "pit"] or
                    self.current_state[next_tile] == CODES["gold"]):
                continue
            break

        if self.current_state[next_tile] == CODES["monster"] or "hero" in INVERSE_CODES[self.current_state[next_tile]]:
            self.current_state[next_tile] = CODES["passage"]

    def score_points(self, action):
        if action == "reset":
            print(f"The map was reset!")
            print(f"-{RESET_PENALTY} points awarded")
            self.points -= RESET_PENALTY
            return
        if self.gold_flag:
            print(f"Got gold!")
            print(f"{GOAL_POINTS} points awarded")
            self.points += GOAL_POINTS
            self.gold_flag = False





# utility functions
# _______________________________________________


def state_to_dict(state):
    dict_to_return = {}
    for row_index, row in enumerate(state):
        for column_index, cell in enumerate(row):
            dict_to_return[(row_index, column_index)] = cell
    return dict_to_return


def wrap_with_walls(map):
    x_dimension = len(map[0]) + 2
    new_map = [[CODES["wall"]] * x_dimension]
    for row in map:
        new_map.append([CODES["wall"]] + list(row) + [CODES["wall"]])
    new_map.append([CODES["wall"]] * x_dimension)
    return new_map


if __name__ == '__main__':
    print(ex3.ids)
    for number, input in enumerate(inputs.inputs):
        my_checker = StochasticChecker(input[0], input[1])
        print(f"Output on input number {number + 1}: {my_checker.check_controller()}")