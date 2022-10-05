from cgi import print_arguments
from random import shuffle
from constants import ACTIONS, MOVE_POS
from finder import Finder
from state import State
from constants import PosType


class SalvadorPlan:
    # Inicia cada lista de ações com uma ordem aleatoria
    RANDOM_INIT_ACTIONS = False

    INITIAL_ACTIONS = ["N", "S", "L", "O", "NE", "NO", "SE", "SO"]

    MOVE_POS = {
        "N": (-1, 0),
        "S": (1, 0),
        "L": (0, 1),
        "O": (0, -1),
        "NE": (-1, 1),
        "NO": (-1, -1),
        "SE": (1, 1),
        "SO": (1, -1),
        "A": (0, 0),
    }

    REVERSE_ACTION = {
        "N": "S",
        "S": "N",
        "L": "O",
        "O": "L",
        "NE": "SO",
        "NO": "SE",
        "SE": "NO",
        "SO": "NE",
    }

    ON_INVALID_ACTION = {
        "N": [
            ("O", "NE"),
            ("L", "NO"),
            ("NO", "L"),
            ("NE", "O"),
            ("A", "NO"),
            ("A", "NE"),
        ],
        "S": [
            ("O", "SE"),
            ("L", "SO"),
            ("SO", "L"),
            ("SE", "O"),
            ("A", "SO"),
            ("A", "SE"),
        ],
        "L": [
            ("N", "SE"),
            ("S", "NE"),
            ("NE", "S"),
            ("SE", "N"),
            ("A", "NE"),
            ("A", "SE"),
        ],
        "O": [
            ("N", "SO"),
            ("S", "NO"),
            ("NO", "S"),
            ("SO", "N"),
            ("A", "NO"),
            ("A", "SO"),
        ],
        "NE": [("N", "L"), ("L", "N")],
        "NO": [("N", "O"), ("O", "N")],
        "SE": [("S", "L"), ("L", "S")],
        "SO": [("O", "S"), ("S", "O")],
    }

    def __init__(
        self, map, vitimas, maxRows, maxColumns, goal, initialState, name="none", mesh="square"
    ):
        """
        Define as variaveis necessárias para a utilização do random plan por um unico agente.
        """
        self.map = map
        self.map_graph = None
        self.vitimas = vitimas
        self.walls = []
        self.maxRows = maxRows
        self.maxColumns = maxColumns
        self.initialState = initialState
        self.currentState = initialState
        self.goalPos = goal
        self.actions = []
        self.vitimas = vitimas
        self.should_pushback = True
        self.__init_map_graph()
        self.__calculate_victims_distance()

    def __init_map_graph(self):
        # print(self.map)
        self.map_graph = []
        # Init empty map graph
        for _ in range(self.maxRows):
            columns = []
            for _ in range(self.maxColumns):
                columns.append([])
            self.map_graph.append(columns)

        for row in range(self.maxRows):
            for col in range(self.maxColumns):
                for action in ACTIONS:
                    d_row, d_col = MOVE_POS[action]
                    s_row = d_row + row
                    s_col = d_col + col
                    # print(action, d_row, d_col, s_row, s_col)
                    if self.__is_valid_pos(s_row, s_col):
                        if self.map[s_row][s_col] != PosType.PAREDE:
                            self.map_graph[row][col].append(action)
        # print(self.map_graph)
        find = Finder(self.map_graph, self.maxRows, self.maxColumns)
        path, cost, states = find.calculate((0, 0), (6, 17))
        # print(states)
        # print(cost)
        # print(path)
        # print(self.map_graph[0][0])
        # print(self.map_graph[7][4])

    def __calculate_victims_distance(self):
        find = Finder(self.map_graph, self.maxRows, self.maxColumns)
        # path, cost, states = find.calculate((0, 0), (6, 17))
        for i in range(len(self.vitimas)):
            # for j in range(len(self.vitimas)):
            print(self.vitimas[i])

    def setWalls(self, walls):
        # Neste modelo o agente não conhece as paredes
        pass
        # row = 0
        # col = 0
        # for i in walls:
        #     col = 0
        #     for j in i:
        #         if j == 1:
        #             self.walls.append((row, col))
        #         col += 1
        #     row += 1

    def updateCurrentState(self, state):
        self.currentState = state

    def isPossibleToMove(self, toState):
        """Verifica se eh possivel ir da posicao atual para o estado (lin, col) considerando
        a posicao das paredes do labirinto e movimentos na diagonal
        @param toState: instancia da classe State - um par (lin, col) - que aqui indica a posicao futura
        @return: True quando é possivel ir do estado atual para o estado futuro"""
        return True
        # Desativado, pois o agente não conhece as bordas
        # vai para fora do labirinto
        # if toState.col < 0 or toState.row < 0:
        #     return False

        # if toState.col >= self.maxColumns or toState.row >= self.maxRows:
        #     return False

        if len(self.walls) == 0:
            return True

        # vai para cima de uma parede
        if (toState.row, toState.col) in self.walls:
            return False

        # vai na diagonal? Caso sim, nao pode ter paredes acima & dir. ou acima & esq. ou abaixo & dir. ou abaixo & esq.
        delta_row = toState.row - self.currentState.row
        delta_col = toState.col - self.currentState.col

        # o movimento eh na diagonal
        if delta_row != 0 and delta_col != 0:
            if (
                self.currentState.row + delta_row,
                self.currentState.col,
            ) in self.walls and (
                self.currentState.row,
                self.currentState.col + delta_col,
            ) in self.walls:
                return False

        return True

    def calculateNextPosition(self):
        """Calcula a posicao futura do agente
        @return: tupla contendo a acao (direcao) e o estado futuro resultante da movimentacao"""
        # print(
        #     self.possible_actions[self.currentState.row][self.currentState.col],
        #     self.pushback_actions[self.currentState.row][self.currentState.col],
        # )
        if len(self.possible_actions[self.currentState.row][self.currentState.col]) > 0:
            self.should_pushback = True
            action = self.possible_actions[self.currentState.row][
                self.currentState.col
            ].pop(0)
        else:
            self.should_pushback = False
            action = self.pushback_actions[self.currentState.row][
                self.currentState.col
            ].pop(-1)
        state = State(
            self.currentState.row + SalvadorPlan.MOVE_POS[action][0],
            self.currentState.col + SalvadorPlan.MOVE_POS[action][1],
        )

        return action, state

    def onInvalidAction(self, action):
        # Eliminar outros estados que possam ser deducidos como inválidos a partir desta ação
        if action in SalvadorPlan.INITIAL_ACTIONS:
            for dst_action, ac_2_remove in SalvadorPlan.ON_INVALID_ACTION[action]:
                row = self.currentState.row + \
                    SalvadorPlan.MOVE_POS[dst_action][0]
                col = self.currentState.col + \
                    SalvadorPlan.MOVE_POS[dst_action][1]
                # Adiciona a parede
                self.walls.append((row, col))
                if row > 0 and col > 0 and row < self.maxRows and col < self.maxColumns:
                    if ac_2_remove in self.possible_actions[row][col]:
                        self.possible_actions[row][col].remove(ac_2_remove)

    def onValidAction(self, action):
        # Eliminar outros estados que possam ser deducidos como válidos a partir desta ação
        # print(action, self.currentState)
        if action in SalvadorPlan.INITIAL_ACTIONS:
            reverse_action = SalvadorPlan.REVERSE_ACTION[action]
            if self.should_pushback:
                self.pushback_actions[self.currentState.row][
                    self.currentState.col
                ].append(reverse_action)
            if (
                reverse_action
                in self.possible_actions[self.currentState.row][self.currentState.col]
            ):
                self.possible_actions[self.currentState.row][
                    self.currentState.col
                ].remove(reverse_action)
            for ac in SalvadorPlan.INITIAL_ACTIONS:
                row = self.currentState.row + SalvadorPlan.MOVE_POS[ac][0]
                col = self.currentState.col + SalvadorPlan.MOVE_POS[ac][1]
                reverse_ac = SalvadorPlan.REVERSE_ACTION[ac]
                if row >= 0 and col >= 0 and row < self.maxRows and col < self.maxColumns and reverse_ac in self.possible_actions[row][col]:
                    self.possible_actions[row][col].remove(reverse_ac)

    def chooseAction(self):
        """
        Eh a acao que vai ser executada pelo agente.
        @return: tupla contendo a acao (direcao) e uma instância da classe State que representa a posição esperada após a execução
        """

        # Tenta encontrar um movimento possivel dentro do tabuleiro
        action = self.calculateNextPosition()

        while not self.isPossibleToMove(action[1]):
            self.onInvalidAction(action[0])
            action = self.calculateNextPosition()

        return action

    def do(self):
        """
        Método utilizado para o polimorfismo dos planos

        Retorna o movimento e o estado do plano (False = nao concluido, True = Concluido)
        """

        nextMove = self.move()
        # self.goalPos == State(nextMove[0][0], nextMove[0][1])
        return (nextMove[1], False)

    def __is_valid_pos(self, row, col):
        return row >= 0 and col >= 0 and row < self.maxRows and col < self.maxColumns
