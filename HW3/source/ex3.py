import random
ids = ["111111111", "111111111"]

class WumpusStochasticController:

    def __init__(self, turn_limit, input_map):
        self.i = 0

    def get_next_action(self, turns_remaining, input_map):
        random.seed(6)
        print("----------")
        for row in input_map:
            print(row)

        self.i += 1
        if self.i == 1:
            return 'move', 11, 'D'
        elif self.i == 2:
            return 'move', 11, 'R'
        elif self.i == 3:
            return 'move', 11, 'R'
        elif self.i == 4:
            return 'move', 11, 'D'
        else:
            return 'shoot', 11, 'D'



# class WumpusStochasticController:
#
#     def __init__(self, turn_limit, input_map):
#         pass
#         # TODO: fill in
#
#     def get_next_action(self, turns_remaining, input_map):
#
#         pass
#         # TODO: fill in
#
#
#
#
#
#         """
#         example random agent
#
#
#         print("-------------")
#         print(f"turns remaining = {turns_remaining}")
#         list_of_heroes = []
#
#         for row in input_map:
#             print(row)
#             for item in row:
#                 for number in [11, 12, 13, 14]:
#                     if number == item:
#                         list_of_heroes.append(number)
#         try:
#             x = random.choice(["move", "shoot"])
#             y = random.choice(list_of_heroes)
#             z = random.choice(["U", "D", "L", "R"])
#             action = (x, y, z)
#         except:
#             action = "reset"
#
#         print(f"chosen action is {action}. \nResults in:")
#         return action
#         """

