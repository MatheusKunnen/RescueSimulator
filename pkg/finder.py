from queue import PriorityQueue
from constants import MOVE_POS
from constants import ACTIONS_COST
from constants import REVERSE_ACTION


class Finder:
    def __init__(self, map, maxRow, maxCol):
        self.map = map
        self.maxRow = maxRow
        self.maxCol = maxCol

    def calculate(self, pos_i, pos_f):
        states = []
        for row in range(self.maxRow):
            cols = []
            for col in range(self.maxCol):
                cols.append(None)
            states.append(cols)

        states[0][0] = Item(pos_i, 0, 0, None)
        frontier = PriorityQueue()
        frontier.put(states[0][0], 0)

        while not frontier.empty():
            state = frontier.get()
            row, col = state.pos
            for action in self.map[row][col]:
                dpos = MOVE_POS[action]
                nr = row + dpos[0]
                nc = col + dpos[1]
                ncost = state.cost + ACTIONS_COST[action]
                if states[nr][nc] is None or ncost < states[nr][nc].cost:
                    if states[nr][nc] is None:
                        states[nr][nc] = Item((nr, nc), 0, 0, None)
                    states[nr][nc].cost = ncost
                    states[nr][nc].priority = ncost + self.h((nr, nc), pos_f)
                    states[nr][nc].predecessor = (row, col)
                    states[nr][nc].reverse_action = REVERSE_ACTION[action]
                    frontier.put(states[nr][nc])
            if state.pos == pos_f:
                break
        path = []
        st = states[pos_f[0]][pos_f[1]]
        while st.predecessor != None and st.pos != pos_i:
            path.append(st.reverse_action)
            st = states[st.predecessor[0]][st.predecessor[1]]
        return states[pos_f[0]][pos_f[1]].cost, path, states

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
