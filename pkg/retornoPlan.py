from constants import ACTIONS, ACTIONS_COST, MOVE_POS
from state import State


class RetornoPlan:

    IDLE_ACTION = ("I", State(0, 0))

    DIAG_COMPONENTS = {
        "NE": ("N", "L"),
        "NO": ("N", "O"),
        "SE": ("S", "L"),
        "SO": ("O", "S"),
    }

    def __init__(self, maxRows, maxColumns, targetState):
        """
        Define as variaveis necessárias para a utilização do random plan por um unico agente.
        """
        self.walls = []
        self.maxRows = maxRows
        self.maxColumns = maxColumns
        self.initialState = None
        self.currentState = None
        self.targetState = targetState
        self.accumulatedCost = 0
        self.inExecution = False

        self.possible_actions_map = [[[]] * self.maxColumns] * self.maxRows
        
        self.max_heuristic = self.maxRows * self.maxColumns * 2 # Valor grande arbitrario
        self.__initHeuristicMap()

    def __initHeuristicMap(self):
        self.heuristicMap = []
        for _ in range(self.maxRows + 2):
            columns = []
            for _ in range(self.maxColumns + 2):
                columns.append(self.max_heuristic)
            self.heuristicMap.append(columns)

        self.__setHeuristic(self.targetState.row, self.targetState.col, 0)
    
    def __getHeuristic(self, row, col):
        # O acesso vai ser deslocado por causa das bordas
        return self.heuristicMap[row + 1][col + 1]
    
    def __setHeuristic(self, row, col, value):
        self.heuristicMap[row + 1][col + 1] = value

    def setWalls(self, _):
        # Neste modelo o agente não conhece as paredes
        pass

    def initPlan(self):
        self.initialState = self.currentState
        self.inExecution = True

    def getCurrentReturnTime(self):
        return self.__getHeuristic(self.currentState.row, self.currentState.col)

    def updateCurrentState(self, state):
        self.currentState = state
        if state != self.targetState:
            self.__updateMaps(state, False)
        
    def __updateMaps(self, state, is_neighbor_update):
        possible_actions = []
        neighbors = []
        cheapest_heuristic = self.max_heuristic

        for direction in ACTIONS:
            neighbor_pos = self.__get_result_state(state, direction)

            can_go_to_neighbor = False
            if self.__isPath(neighbor_pos):
                if direction in RetornoPlan.DIAG_COMPONENTS:
                    component1, component2 = RetornoPlan.DIAG_COMPONENTS[direction]
                    diag1 = self.__get_result_state(state, component1)
                    diag2 = self.__get_result_state(state, component2)
                    if self.__isPath(diag1) and self.__isPath(diag2):
                        can_go_to_neighbor = True
                else:
                    can_go_to_neighbor = True

            neighbor_heuristic = self.__getHeuristic(neighbor_pos.row, neighbor_pos.col)

            if can_go_to_neighbor:
                possible_actions.append(direction)
                neighbors.append(neighbor_pos)
                current_heuristic = neighbor_heuristic + ACTIONS_COST[direction]
                if current_heuristic <= cheapest_heuristic:
                    cheapest_heuristic = current_heuristic
        
        current_heuristic = self.__getHeuristic(state.row, state.col)
        if cheapest_heuristic > current_heuristic:
            cheapest_heuristic = current_heuristic

        self.__setHeuristic(state.row, state.col, cheapest_heuristic)
        if not is_neighbor_update:
            self.possible_actions_map[state.row][state.col] = possible_actions
            for neighbor in neighbors:
                self.__updateMaps(neighbor, True)

    def __get_result_state(self, state, direction):
        step = MOVE_POS[direction]
        return State(state.row + step[0], state.col + step[1])

    def __isPath(self, state):
        heuristic = self.__getHeuristic(state.row, state.col)
        return heuristic != self.max_heuristic

    def isPossibleToMove(self, _):
        """Verifica se eh possivel ir da posicao atual para o estado (lin, col) considerando
        a posicao das paredes do labirinto e movimentos na diagonal
        @param toState: instancia da classe State - um par (lin, col) - que aqui indica a posicao futura
        @return: True quando é possivel ir do estado atual para o estado futuro"""
        # Desativado, pois o agente não conhece as bordas
        return True

    def getCheapestPathAction(self):
        """Calcula a posicao futura do agente
        @return: tupla contendo a acao (direcao) e o estado futuro resultante da movimentacao"""
        
        possible_actions = self.possible_actions_map[self.currentState.row][self.currentState.col]
        if len(possible_actions) > 0:
            cheapest_action = possible_actions[0]
            result_state = None
            lower_cost = self.max_heuristic

            for action in possible_actions:
                state = self.__get_result_state(self.currentState, action)
                total_cost = self.accumulatedCost + self.__getHeuristic(state.row, state.col)
                if total_cost < lower_cost:
                    lower_cost = total_cost
                    cheapest_action = action
                    result_state = state

        else:
            raise Exception("Estado invalido, no retorno sempre deve haver acoes possiveis")

        return cheapest_action, result_state

    def onInvalidAction(self, _):
        pass

    def onValidAction(self, _):
        # TODO: add to cost accumulator
        pass

    def chooseAction(self):
        """
        Eh a acao que vai ser executada pelo agente.
        @return: tupla contendo a acao (direcao) e uma instância da classe State que representa a posição esperada após a execução
        """

        # Tenta encontrar um movimento possivel dentro do tabuleiro
        if self.currentState != self.targetState:
            action = self.getCheapestPathAction()
        else:
            action = RetornoPlan.IDLE_ACTION
        return action

    def do(self):
        """
        Método utilizado para o polimorfismo dos planos

        Retorna o movimento e o estado do plano (False = nao concluido, True = Concluido)
        """

        nextMove = self.move()
        # self.goalPos == State(nextMove[0][0], nextMove[0][1])
        return (nextMove[1], False)
