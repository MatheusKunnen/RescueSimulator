
from genericpath import exists
import random
from tkinter import VERTICAL
from finder import Finder


class SalvadorAG:

    def __init__(self, map_graph, maxRows, maxCols, distances, vitimas, time, base, m=None):
        self.map_graph = map_graph
        self.distances = distances
        self.maxRows = maxRows
        self.maxCols = maxCols
        self.time = time
        self.vitimas = [(i, p, s) for i, (p, s) in enumerate(vitimas)]
        self.base = base
        self.m = m
        self.finder = Finder(self.map_graph, self.maxRows, self.maxCols)
        self.__init_fit_function()
        self.__init_params()
        self.__generate_population()

    def get_best_path(self):
        return self.population[0].path

    def calculate(self):
        self.__sort_population()
        it = 0
        max_fit = self.population[0].fit
        # print("C", max_fit, len(self.population))
        while it < self.max_it:
            self.__evolve()
            self.__sort_population()
            # for i, p in enumerate(self.population):
            # print(p.cost, p.fit)/
            if self.population[0].fit > max_fit:
                it = 0
                max_fit = self.population[0].fit
            else:
                it += 1

    def __evolve(self):
        new_population = self.population[:-round((len(self.population)/2))]
        max_fit = new_population[0].fit
        # print("E", max_fit, len(self.population))

        i = 0
        while len(new_population) < self.population_size:
            if i + 1 < len(new_population):
                j = i + random.randint(i+1, len(new_population)-1)
                n_fit = new_population[i].fit/(max_fit)
                ind = self.__crossover(
                    new_population[i], new_population[j], n_fit, self.mutation_prob)
                new_population.append(ind)
            else:
                ind = self.__mutate(new_population[i], self.mutation_prob)
                new_population.append(ind)
        self.population = new_population

    def __crossover(self, ind_a, ind_b, prob_c, prob_m):
        if prob_c is None:
            prob_c = self.crossover_prob
        if prob_m is None:
            prob_m = self.mutation_prob
        if random.uniform(0, 1) > prob_c:
            if random.uniform(0, 1) > 0.5:
                return self.__mutate(ind_a, prob_m)
            else:
                return self.__mutate(ind_b, prob_m)
        v_a = random.sample(
            ind_a.vitimas, random.randint(0, len(ind_a.vitimas))).copy()
        v_b = random.sample(
            ind_a.vitimas, random.randint(0, len(ind_a.vitimas))).copy()
        # if random.uniform(0, 1) > 0.5:

        n_vitimas = v_a
        for vitima in v_b:
            exits = False
            for v in n_vitimas:
                exits = exits or v[0] == vitima[0]
            if not exits:
                n_vitimas.append(vitima)
        # else:
        c, p = self.__calculate_chromosome_cost(n_vitimas)
        while c > self.time:
            n_vitimas = random.sample(n_vitimas, len(n_vitimas)-1)
            c, p = self.__calculate_chromosome_cost(n_vitimas)
        fit = self.fit_function(n_vitimas)/c
        chromosome = Chromosome(n_vitimas, c, p, fit)
        return self.__mutate(chromosome, prob_m)

    def __mutate(self, individuo, prob_m):
        if random.uniform(0, 1) > prob_m:
            return individuo
        n_vitimas = individuo.vitimas
        # swap mutation
        if random.uniform(0, 1) <= self.prob_m_swap:
            n_vitimas = self.__m_swap_vitimas(n_vitimas)
        # add/remove mutation
        if random.uniform(0, 1) <= self.prob_m_add_rm:
            n_vitimas = self.__m_add_rm_vitimas(n_vitimas, 0.5)
        c, p = self.__calculate_chromosome_cost(n_vitimas)
        while c > self.time:
            # swap mutation
            if random.uniform(0, 1) <= self.prob_m_swap:
                n_vitimas = self.__m_swap_vitimas(n_vitimas)
            # add/remove mutation
            if random.uniform(0, 1) <= self.prob_m_add_rm:
                n_vitimas = self.__m_add_rm_vitimas(n_vitimas, 0.75)
            n_vitimas = random.sample(n_vitimas, len(n_vitimas)-1)
            c, p = self.__calculate_chromosome_cost(n_vitimas)
        fit = self.fit_function(n_vitimas)/c
        chromosome = Chromosome(n_vitimas, c, p, fit)
        return self.__mutate(chromosome, prob_m)

    def __m_swap_vitimas(self, vitimas):
        # return vitimas
        v_a = vitimas.index(random.choice(vitimas))
        v_b = vitimas.index(random.choice(vitimas))
        n_vitimas = vitimas.copy()
        aux = n_vitimas[v_a]
        n_vitimas[v_a] = n_vitimas[v_b]
        n_vitimas[v_b] = aux
        return n_vitimas

    def __m_add_rm_vitimas(self, vitimas, add_prob=0.5):
        if random.uniform(0, 1) < add_prob:
            # Adiciona
            if len(vitimas) == len(self.vitimas):
                return vitimas
            n_vitima = random.choice(self.vitimas)
            aux = [v for v in vitimas if v[0] == n_vitima[0]]
            while len(aux) > 0:
                n_vitima = random.choice(self.vitimas)
                aux = [v for v in vitimas if v[0] == n_vitima[0]]
            n_vitimas = vitimas.copy()
            n_vitimas.append(n_vitima)
            return n_vitimas
        else:
            if len(vitimas) < 2:
                return vitimas
            # Remove
            n_vitimas = random.sample(vitimas, len(vitimas)-1).copy()
            return n_vitimas

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
            self.population.append(chromosome)
        self.__sort_population()
        # for i, p in enumerate(self.population):
        # print(p.cost, p.fit)

    def __sort_population(self):
        self.population.sort(key=lambda p: p.fit, reverse=True)

    def __generate_chromosome(self):
        valid = False
        chromosome = None
        vitimas = self.vitimas.copy()
        random.shuffle(vitimas)
        while not valid:
            vitimas.pop()
            c, p = self.__calculate_chromosome_cost(vitimas)
            if c <= self.time:
                fit = self.fit_function(vitimas)/c
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
                ida, posa, _ = vitima_ant
                c, p, _ = self.finder.calculate(
                    posa, pos)  # self.distances[ida][id]
                # c, p = self.distances[ida][id]
                cost += c
                path.extend(p)
            else:
                # Custo saindo da base
                c, p, _ = self.finder.calculate(self.base, pos)
                cost += c
                path.extend(p)
            vitima_ant = vitima
            # break
        # Calcula custo para volver a base
        _, pv, _ = vitima_ant
        c, p, _ = self.finder.calculate(pv, self.base)
        print(self.base, pv, p, self.map_graph[pv[0]][pv[1]])
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
        self.prob_m_swap = 0.25
        self.prob_m_add_rm = 0.25
        self.max_it = 2


class Chromosome:
    def __init__(self, vitimas, cost, path, fit):
        self.vitimas = vitimas
        self.cost = cost
        self.path = path
        self.fit = fit

    def __lt__(self, other):
        self.fit < other.fit
