from cgi import print_arguments
from random import shuffle
from constants import ACTIONS, MOVE_POS
from finder import Finder
from constants import REVERSE_ACTION
from salvadorAG import SalvadorAG
from state import State
from constants import PosType


class SalvadorPlan:

    def __init__(
        self, map, vitimas, maxRows, maxColumns, time, initialState, name="none", mesh="square"
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
        self.time = time
        self.initialState = initialState
        self.currentState = initialState
        self.actions = []
        self.vitimas = vitimas
        self.should_pushback = True
        self.distances = []
        self.__init_map_graph()
        self.__calculate_victims_distance()
        self.__init_ag()

    def __init_ag(self):
        self.ag = SalvadorAG(self.map_graph, self.maxRows, self.maxColumns, self.distances,
                             self.vitimas, self.time, (self.initialState.row, self.initialState.col))
        self.ag.calculate()
        self.actions = self.ag.get_best_path()
        print(self.actions)

    def __init_map_graph(self):
        self.map_graph = []
        # Init empty map graph
        for _ in range(self.maxRows):
            columns = []
            for _ in range(self.maxColumns):
                columns.append([])
            self.map_graph.append(columns)

        for row in range(self.maxRows):
            for col in range(self.maxColumns):
                for action in ["N", "S", "L", "O"]:  # ACTIONS:
                    d_row, d_col = MOVE_POS[action]
                    s_row = d_row + row
                    s_col = d_col + col
                    if self.__is_valid_pos(s_row, s_col):
                        if self.map[s_row][s_col] != PosType.PAREDE:
                            self.map_graph[row][col].append(action)

    def __calculate_victims_distance(self):
        find = Finder(self.map_graph, self.maxRows, self.maxColumns)
        for _ in range(len(self.vitimas)):
            cols = []
            for _ in range(len(self.vitimas)):
                cols.append(None)
            self.distances.append(cols)

        for i in range(len(self.vitimas)):
            pos_i, _ = self.vitimas[i]
            self.distances[i][i] = (0, [])
            for j in range(i+1, len(self.vitimas)):
                pos_j, _ = self.vitimas[j]
                cost, path, _ = find.calculate(pos_i, pos_j)
                self.distances[i][j] = (cost, path)
                cost, path, _ = find.calculate(pos_j, pos_i)
                self.distances[j][i] = (cost, path)

    def setWalls(self, walls):
        # Neste modelo o agente não conhece as paredes
        pass

    def updateCurrentState(self, state):
        self.currentState = state

    def isPossibleToMove(self, toState):
        """Verifica se eh possivel ir da posicao atual para o estado (lin, col) considerando
        a posicao das paredes do labirinto e movimentos na diagonal
        @param toState: instancia da classe State - um par (lin, col) - que aqui indica a posicao futura
        @return: True quando é possivel ir do estado atual para o estado futuro"""
        # Desativado, pois o agente não conhece as bordas
        return True

    def onInvalidAction(self, action):
        return

    def onValidAction(self, action):
        return

    def chooseAction(self):
        """
        Eh a acao que vai ser executada pelo agente.
        @return: tupla contendo a acao (direcao) e uma instância da classe State que representa a posição esperada após a execução
        """

        if len(self.actions) > 0:
            action = self.actions.pop()
            state = State(
                self.currentState.row + MOVE_POS[action][0],
                self.currentState.col + MOVE_POS[action][1],
            )
            return action, state
        else:
            return None

    def do(self):
        """
        Método utilizado para o polimorfismo dos planos

        Retorna o movimento e o estado do plano (False = nao concluido, True = Concluido)
        """

        nextMove = self.move()
        return (nextMove[1], False)

    def __is_valid_pos(self, row, col):
        return row >= 0 and col >= 0 and row < self.maxRows and col < self.maxColumns
