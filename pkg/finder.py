from queue import PriorityQueue
from typing import TypeVar
from constants import MOVE_POS
from constants import ACTIONS_COST
from constants import REVERSE_ACTION
Location = TypeVar('Location')


class Finder:
    def __init__(self, map, maxRow, maxCol, m=None):
        self.m = m
        self.map = map
        self.maxRow = maxRow
        self.maxCol = maxCol

    def calculate(self, pos_i, pos_f):
        # frontier = PriorityQueue()
        # frontier.put(pos_i, 0)
        # came_from: dict[Location, Location] = {}
        # cost_so_far: dict[Location, float] = {}
        # came_from[pos_i] = None
        # cost_so_far[pos_i] = 0

        # while not frontier.empty():
        #     current = frontier.get()

        #     if current == pos_f:
        #         break

        #     for action in self.map[current[0]][current[1]]:
        #         dpos = MOVE_POS[action]
        #         nr = current[0] + dpos[0]
        #         nc = current[0] + dpos[1]
        #         next = (nr, nc)
        #         # for next in graph.neighbors(current):
        #         # graph.cost(current, (nr, nc))
        #         new_cost = cost_so_far[current] + ACTIONS_COST[action]
        #         if next not in cost_so_far or new_cost < cost_so_far[next]:
        #             cost_so_far[next] = new_cost
        #             priority = new_cost + self.h(next, pos_f)
        #             frontier.put(next, priority)
        #             came_from[next] = current
        #             action[next] = (REVERSE_ACTION[action])
        #             current = pos_f
        # path = []
        # if pos_f not in came_from:  # no path was found
        #     return -1, [], None
        # while current != pos_i:
        #     path.append(action[current])
        #     current = came_from[current]
        # path.append(pos_i)  # optional
        # path.reverse()  # optional
        # # return path

        # return cost_so_far[pos_f], path, None

        states = []
        for row in range(self.maxRow):
            cols = []
            for col in range(self.maxCol):
                cols.append(None)
            states.append(cols)

        states[0][0] = Item(pos_i, 0, 0, None)
        stt = {}
        stt[pos_i] = Item(pos_i, 0, 0, None)
        frontier = PriorityQueue()
        frontier.put(states[0][0], 0)

        while not frontier.empty():
            state = frontier.get()
            row, col = state.pos
            if state.pos == pos_f:
                print(state.predecessor, state.reverse_action, state.pos, pos_f)
                break

            for action in self.map[row][col]:
                dpos = MOVE_POS[action]
                nr = row + dpos[0]
                nc = col + dpos[1]
                next = (nr, nc)
                ncost = state.cost + ACTIONS_COST[action]
                if next not in stt or ncost < stt[next].cost:
                    # if states[nr][nc] is None or ncost < states[nr][nc].cost:
                    if next not in stt:
                        # if states[nr][nc] is None:
                        stt[next] = Item((nr, nc), 0, 0, None)
                    stt[next].cost = ncost
                    stt[next].priority = ncost + \
                        self.h((nr, nc), (pos_f[0], pos_f[1]))
                    stt[next].predecessor = (row, col)
                    stt[next].reverse_action = REVERSE_ACTION[action]
                    frontier.put(
                        Item((nr, nc), ncost, stt[next].priority, (row, col), REVERSE_ACTION[action]))

        path = []
        st = stt[pos_f]  # states[pos_f[0]][pos_f[1]]
        # print(st.pos, st.reverse_action)
        while st.predecessor != None and st.pos != pos_i:
            path.append(st.reverse_action)
            # states[st.predecessor[0]][st.predecessor[1]]
            st = stt[st.predecessor]
        # if st.pos == pos_i and st.predecessor != None:
            # path.append(st.reverse_action)
        path.reverse()
        # print("A", pos_i, pos_f, path)
        return stt[pos_f].cost, path, states
        # return states[pos_f[0]][pos_f[1]].cost, path, states

    def h(self, pos_i, pos_f):
        return abs(pos_f[0] - pos_i[0]) + abs(pos_f[1] - pos_i[1])


class Item:
    def __init__(self, pos, cost, priority, predecessor, reverse_action=None):
        self.pos = pos
        self.cost = cost
        self.priority = priority
        self.predecessor = predecessor
        self.reverse_action = reverse_action

    def __lt__(self, other):
        return self.priority < other.priority
