# AGENTE Explorador
# Importa Classes necessarias para o funcionamento
from constants import get_label_gravidade
from model import Model
from retornoPlan import RetornoPlan
from problem import Problem
from state import State
from random import randint
from constants import PosType

# Importa o algoritmo para o plano
from exploradorPlan import ExploradorPlan


# Classe que define o Agente
class AgentExplorador:

    CUSTO_VITIMA = 2

    def __init__(self, model, configDict):
        """
        Construtor do agente explorador
        @param model referencia o ambiente onde o agente estah situado
        """

        self.model = model

        # Obtem o tempo que tem para executar
        self.tempoTotal = configDict["Te"]
        self.tl = self.tempoTotal
        print("Tempo disponivel: ", self.tl)

        # Pega o tipo de mesh, que está no model (influência na movimentação)
        self.mesh = self.model.mesh

        # Cria a instância do problema na mente do agente (sao suas crencas)
        self.prob = Problem()
        self.prob.createMaze(model.rows, model.columns, model.maze)

        # O agente le sua posica no ambiente por meio do sensor
        initial = self.positionSensor()
        self.prob.defInitialState(initial.row, initial.col)
        print("*** Estado inicial do agente: ", self.prob.initialState)

        # Define o estado atual do agente = estado inicial
        self.currentState = self.prob.initialState

        # Define o estado objetivo:
        # definimos um estado objetivo aleatorio
        # self.prob.defGoalState(randint(0,model.rows-1), randint(0,model.columns-1))

        # definimos um estado objetivo que veio do arquivo ambiente.txt
        self.prob.defGoalState(
            model.maze.board.posGoal[0], model.maze.board.posGoal[1])
        # print("*** Objetivo do agente: ", self.prob.goalState)
        print(
            "*** Total de vitimas existentes no ambiente: ",
            self.model.getNumberOfVictims(),
        )

        """
        DEFINE OS PLANOS DE EXECUÇÃO DO AGENTE
        """

        # Custo da solução
        self.costAll = 0

        # Cria a instancia do plano para se movimentar aleatoriamente no labirinto (sem nenhuma acao)
        self.plan = ExploradorPlan(
            model.rows, model.columns, self.prob.goalState, initial, "goal", self.mesh
        )

        self.returnPlan = RetornoPlan(model.rows, model.columns, initial)

        # adicionar crencas sobre o estado do ambiente ao plano - neste exemplo, o agente faz uma copia do que existe no ambiente.
        # Em situacoes de exploracao, o agente deve aprender em tempo de execucao onde estao as paredes
        self.plan.setWalls(model.maze.walls)

        # Adiciona o(s) planos a biblioteca de planos do agente
        self.libPlan = [self.plan, self.returnPlan]

        # inicializa acao do ciclo anterior com o estado esperado
        self.previousAction = "nop"  # nenhuma (no operation)
        self.expectedState = self.currentState

        # inicia vetor de vitimas
        self.__vitimas_id = []
        self.__vitimas = []
        # inicia mapa
        self.__init_map()

    # Metodo que define a deliberacao do agente
    def deliberate(self):
        # Adiciona estado como livre no mapa
        self.__updateMap()

        # Verifica se há algum plano a ser executado
        if len(self.libPlan) == 0:
            return -1  # fim da execucao do agente, acabaram os planos

        if self.tl <= 0.5:
            # print(self.__map)
            print(len(self.__vitimas), self.model.getNumberOfVictims())
            # self.__init_map()
            return -1

        self.plan = self.libPlan[0]

        print("\n*** Inicio do ciclo raciocinio ***")
        print("Pos agente no amb.: ", self.positionSensor())

        # Redefine o estado atual do agente de acordo com o resultado da execução da ação do ciclo anterior
        self.currentState = self.positionSensor()
        # atualiza o current state nos planos
        self.updateLibPlan()
        print("Ag cre que esta em: ", self.currentState)

        # Verifica se a execução do acao do ciclo anterior funcionou ou nao
        if not (self.currentState == self.expectedState):
            self.plan.onInvalidAction(self.previousAction)
            print(
                "---> erro na execucao da acao ",
                self.previousAction,
                ": esperava estar em ",
                self.expectedState,
                ", mas estou em ",
                self.currentState,
            )
        else:
            self.plan.onValidAction(self.previousAction)

        # consome o tempo gasto
        self.tl -= self.prob.getActionCost(self.previousAction)
        self.costAll += self.prob.getActionCost(self.previousAction)
        print("Tempo disponivel: ", self.tl)

        # Funcionou ou nao, vou somar o custo da acao com o total
        print("Custo até o momento (com a ação escolhida):",
              self.tempoTotal - self.tl)

        # Verifica se precisa retorna pra base
        return_time = self.returnPlan.getCurrentReturnTime()
        print(f"Return time: {return_time}")
        if not self.returnPlan.inExecution:
            if self.tl - 1.5 <= return_time:
                self.__enterInReturnMode()
            else:
                # Verifica se tem vitima na posicao atual
                self.__checkVitima()

        # Define a proxima acao a ser executada
        # currentAction eh uma tupla na forma: <direcao>, <state>
        result = self.plan.chooseAction()
        print(
            "Ag deliberou pela acao: ",
            result[0],
            ", o estado resultado esperado é: ",
            result[1],
        )

        # Executa esse acao, atraves do metodo executeGo
        self.executeGo(result[0])
        self.previousAction = result[0]
        self.expectedState = result[1]

        return 1

    def __enterInReturnMode(self):
        print("Entering return mode")
        self.libPlan.pop(0)
        self.returnPlan.initPlan()
        self.plan = self.returnPlan

    def __checkVitima(self):
        """
        Verifica se tem vitima na posicao atual
        """
        victimId = self.victimPresenceSensor()
        if victimId <= 0:
            return

        # Verifica se já descubrimos a vitima
        if victimId in self.__vitimas_id:
            return

        if self.tl < 2:
            return

        # Lê sinais vitais
        sinais_vitais = self.victimVitalSignalsSensor(victimId)

        if len(sinais_vitais) <= 0:
            return
        # Utiliza tempo para ler
        self.tl -= AgentExplorador.CUSTO_VITIMA
        self.costAll += AgentExplorador.CUSTO_VITIMA

        # Adiciona vitima
        self.__vitimas_id.append(victimId)
        self.__vitimas.append(
            ((self.currentState.row, self.currentState.col), sinais_vitais)
        )

        print(
            "vitima encontrada em ",
            self.currentState,
            " id: ",
            victimId,
            " sinais vitais: ",
            sinais_vitais,
        )

    # Metodo que executa as acoes
    def executeGo(self, action):
        """Atuador: solicita ao agente físico para executar a acao.
        @param direction: Direcao da acao do agente {"N", "S", ...}
        @return 1 caso movimentacao tenha sido executada corretamente"""

        # Passa a acao para o modelo
        result = self.model.go(action)

        # Se o resultado for True, significa que a acao foi completada com sucesso, e ja pode ser removida do plano
        # if (result[1]): ## atingiu objetivo ## TACLA 20220311
        ##    del self.plan[0]
        ##    self.actionDo((2,1), True)

    # Metodo que pega a posicao real do agente no ambiente

    def positionSensor(self):
        """Simula um sensor que realiza a leitura do posição atual no ambiente.
        @return instancia da classe Estado que representa a posição atual do agente no labirinto."""
        pos = self.model.agentPos
        return State(pos[0], pos[1])

    def victimPresenceSensor(self):
        """Simula um sensor que realiza a deteccao de presenca de vitima na posicao onde o agente se encontra no ambiente
        @return retorna o id da vítima"""
        return self.model.isThereVictim()

    def victimVitalSignalsSensor(self, victimId):
        """Simula um sensor que realiza a leitura dos sinais da vitima
        @param o id da vítima
        @return a lista de sinais vitais (ou uma lista vazia se não tem vítima com o id)"""
        return self.model.getVictimVitalSignals(victimId)

    def victimDiffOfAcessSensor(self, victimId):
        """Simula um sensor que realiza a leitura dos dados relativos à dificuldade de acesso a vítima
        @param o id da vítima
        @return a lista dos dados de dificuldade (ou uma lista vazia se não tem vítima com o id)"""
        return self.model.getDifficultyOfAcess(victimId)

    def get_gv(self):
        gv = [0, 0, 0, 0]
        for i in self.__vitimas_id:
            sinais = self.model.getVictimVitalSignals(i)
            if len(sinais) > 0:
                gv[get_label_gravidade(sinais)-1] += 1
        max_grav_vitimas = 0
        for i in range(len(gv)):
            max_grav_vitimas += (4-i) * gv[i]
            # max_grav_vitimas += (i+1) * gv[i]
        return max_grav_vitimas
    # Metodo que atualiza a biblioteca de planos, de acordo com o estado atual do agente

    def updateLibPlan(self):
        for i in self.libPlan:
            i.updateCurrentState(self.currentState)

    def actionDo(self, posAction, action=True):
        self.model.do(posAction, action)

    def getMap(self):
        return self.__map

    def getVitimas(self):
        return self.__vitimas

    def __updateMap(self):
        self.__map[self.currentState.row][self.currentState.col] = PosType.LIVRE

    def __init_map(self):
        """
        Inicia matriz do mapa do ambiente
        """
        self.__map = []
        for _ in range(self.model.rows):
            columns = []
            for _ in range(self.model.columns):
                columns.append(PosType.PAREDE)
            self.__map.append(columns)
