from agentExplorador import AgentExplorador
from model import Model
from Configuration import Configuration
import sys
import os
import time

# Importa as classes que serao usadas
# sys.path.append(os.path.join("pkg"))


# Metodo utilizado para permitir que o usuario construa o labirindo clicando em cima
def buildMaze(model):
    model.drawToBuild()
    step = model.getStep()
    while step == "build":
        model.drawToBuild()
        step = model.getStep()
    # Atualiza o labirinto
    model.updateMaze()


def main():

    # Lê arquivo config.txt
    # arq = open(os.path.join("config_data", "config.txt"), "r")
    # configDict = {}
    # for line in arq:
    #     # O formato de cada linha é:var=valor
    #     # As variáveis são
    #     # maxLin, maxCol que definem o tamanho do labirinto
    #     # Tv e Ts: tempo limite para vasculhar e tempo para salvar
    #     # Bv e Bs: bateria inicial disponível ao agente vasculhador e ao socorrista
    #     # Ks :capacidade de carregar suprimentos em número de pacotes (somente para o ag. socorrista)

    #     values = line.split("=")
    #     configDict[values[0]] = int(values[1])
    config = Configuration(
        "./config_data/ambiente.txt", "./config_data/sinais_vitais.txt"
    )
    # return
    # print("dicionario config: ", configDict)

    # Cria o ambiente (modelo) = Labirinto com suas paredes
    mesh = "square"

    # nome do arquivo de configuracao do ambiente - deve estar na pasta <proj>/config_data
    loadMaze = "ambiente"

    # config.getMaxFilas(), config.getMaxColumnas(), mesh, loadMaze)
    model = Model(config)
    buildMaze(model)

    model.maze.board.posAgent
    model.maze.board.posGoal
    # Define a posição inicial do agente no ambiente - corresponde ao estado inicial
    model.setAgentPos(config.ambiente["Base"][0], config.ambiente["Base"][0])
    # model.maze.board.posAgent[0], model.maze.board.posAgent[1])
    model.setGoalPos(model.maze.board.posGoal[0], model.maze.board.posGoal[1])
    model.draw()

    # Cria um agente
    explorador = AgentExplorador(model, config.ambiente)

    # Ciclo de raciocínio do agente
    explorador.deliberate()
    while explorador.deliberate() != -1:
        model.draw()
        # para dar tempo de visualizar as movimentacoes do agente no labirinto
        time.sleep(.05)
    model.draw()


if __name__ == "__main__":
    main()
