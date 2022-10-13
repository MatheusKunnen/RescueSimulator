from agentExplorador import AgentExplorador
from agentSalvador import AgentSalvador
from model import Model
from Configuration import Configuration
from constants import get_label_gravidade
import time


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
    # Leitura da configuração
    config = Configuration(
        "./config_data/ambiente.txt", "./config_data/sinais_vitais.txt"
    )

    model = Model(config)
    buildMaze(model)

    # Define a posição inicial do agente no ambiente - corresponde ao estado inicial
    model.setAgentPos(config.ambiente["Base"][0], config.ambiente["Base"][1])
    model.setGoalPos(model.maze.board.posGoal[0], model.maze.board.posGoal[1])
    model.draw()

    # Cria o agente explorador
    explorador = AgentExplorador(model, config.ambiente)

    # Ciclo de raciocínio do agente
    explorador.deliberate()
    while explorador.deliberate() != -1:
        model.draw()
        # para dar tempo de visualizar as movimentacoes do agente no labirinto
        time.sleep(.05)
    print("Fim exploracao")

    model.setAgentPos(config.ambiente["Base"][0], config.ambiente["Base"][0])
    salvador = AgentSalvador(
        explorador.getMap(), explorador.getVitimas(), model, config.ambiente)
    while salvador.deliberate() != -1:
        model.draw()
        # para dar tempo de visualizar as movimentacoes do agente no labirinto
        time.sleep(.05)
    print("Fim da salvacao")
    gv = [0, 0, 0, 0]
    for i in range(model.getNumberOfVictims()-1):
        sinais = model.getVictimVitalSignals(i)
        if len(sinais) > 0:
            gv[get_label_gravidade(sinais)-1] += 1
    max_grav_vitimas = 0
    for i in range(len(gv)):
        max_grav_vitimas += (i+1) * gv[i]

    print("Vitimas encontradas", len(explorador.getVitimas()),
          "/", model.getNumberOfVictims())
    print("Vitimas salvadas", salvador.getNVitimas(),
          "/", len(explorador.getVitimas()))
    print("pve", len(explorador.getVitimas())/model.getNumberOfVictims())
    print("tve", explorador.costAll/len(explorador.getVitimas()))
    print("veg", explorador.get_gv()/max_grav_vitimas)
    print("pvs", salvador.getNVitimas()/model.getNumberOfVictims())
    if salvador.getNVitimas() > 0:
        print("tsv", salvador.costAll/salvador.getNVitimas())
    else:
        print("tsv", "N/A")
    print("vsg", salvador.get_gv()/max_grav_vitimas)

    model.draw()


if __name__ == "__main__":
    main()
