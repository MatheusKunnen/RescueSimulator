
import random
from finder import Finder


class SalvadorAG:

    def __init__(self, map_graph, maxRows, maxCols, distances, vitimas, time, base):
        self.map_graph = map_graph
        self.distances = distances
        self.maxRows = maxRows
        self.maxCols = maxCols
        self.time = time
        self.vitimas = [(i, p, s) for i, (p, s) in enumerate(vitimas)]
        self.base = base
        self.finder = Finder(self.map_graph, self.maxRows, self.maxCols)
        self.__init_fit_function()
        self.__init_params()
        self.__generate_population()

    def crossover(self, ind_a, ind_b):
        pass

    def mutate(self, individuo):
        pass

    def fit_function(self, vitimas):
        class_vitimas = [0, 0, 0, 0]
        for vitima in vitimas:
            _, _, sinais = vitima
            class_vitimas[self.get_label_gravidade(sinais)-1] += 1
        aux = 0
        for i, n in enumerate(class_vitimas):
            aux += (i+1)*n
        return aux*self.fit_multiplier

    def __init_fit_function(self):
        self.fit_multiplier = 1
        self.fit_multiplier = self.fit_function(self.vitimas)
        self.fit_multiplier = 1/self.fit_multiplier

    def __generate_population(self):
        self.population = []
        while len(self.population) < self.population_size:
            chromosome = self.__generate_chromosome()
            print("C", chromosome.cost, chromosome.fit)
            self.population.append(chromosome)
        self.__sort_population()
        for p in self.population:
            print(p.cost, p.fit)

    def __sort_population(self):
        self.population.sort(key=lambda p: p.fit)

    def __generate_chromosome(self):
        valid = False
        chromosome = None
        vitimas = self.vitimas.copy()
        random.shuffle(vitimas)
        while not valid:
            vitimas.pop()
            c, p = self.__calculate_chromosome_cost(vitimas)
            if c <= self.time:
                fit = self.fit_function(vitimas)
                chromosome = Chromosome(vitimas, c, p, fit)
                valid = True
        return chromosome

    def __is_valid_chromosome(self, chromosome):
        cost, _ = self.__calculate_chromosome_cost(chromosome)
        return cost < self.time

    def __calculate_chromosome_cost(self, vitimas):
        if len(vitimas) <= 0:
            return 0, []
        vitima_ant = None
        cost = 0
        path = []
        for vitima in vitimas:
            id, pos, _ = vitima
            if vitima_ant:
                # Custo entre as vitimas
                ida, _, _ = vitima_ant
                c, p = self.distances[ida][id]
                cost += c
                path.extend(p)
            else:
                # Custo saindo da base
                c, p, _ = self.finder.calculate(self.base, pos)
                cost += c
                path.extend(p)
            vitima_ant = vitima
        # Calcula custo para volver a base
        _, pv, _ = vitima_ant
        c, p, _ = self.finder.calculate(pv, self.base)
        cost += c
        path.extend(p)
        return cost, path

    def get_label_gravidade(self, sinais_vitais):
        gravidade = sinais_vitais[len(sinais_vitais) - 1]
        if len(sinais_vitais) > 7:
            gravidade = sinais_vitais[len(sinais_vitais) - 2]
        label = 1
        if gravidade > 75:
            label += 1
        if gravidade > 50:
            label += 1
        if gravidade > 25:
            label += 1
        return label

    def __init_params(self):
        self.min_v_size = 1
        self.max_v_size = len(self.vitimas)
        self.mutation_prob = 0.2
        self.crossover_prob = 0.5
        self.population_size = len(self.vitimas) * 2


class Chromosome:
    def __init__(self, vitimas, cost, path, fit):
        self.vitimas = vitimas
        self.cost = cost
        self.path = path
        self.fit = fit

    def __lt__(self, other):
        self.fit < other.fit
