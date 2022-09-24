class Configuration:

    def __init__(self, ambiente_path, sinais_vitais_path):
        self.ambiente_path = ambiente_path
        self.sinais_vitais_path = sinais_vitais_path
        self.ambiente = {}
        self.sinais_vitais = []
        self.__load()

    def __load(self):
        self.__load_ambiente()
        self.__load_sinais_vitais()

    def __load_ambiente(self):
        ambiente_file = open(self.ambiente_path, "r")
        lines = ambiente_file.readlines()
        ambiente_file.close()
        for line in lines:
            param, *values = line.replace('\n', '').split(' ')
            value = None
            if (param == 'Te' or param == 'Ts' or param == 'XMax' or param == "YMax"):
                value = int(values[0])
            elif (param == 'Base'):
                x, y, *_ = values[0].split(',')
                value = [int(x), int(y)]
            elif (param == 'Vitimas' or param == 'Parede'):
                value = []
                for pos in values:
                    x, y, *_ = pos.split(',')
                    value.append([int(x), int(y)])
            else:
                raise Exception('Parametro inválido!')
            self.ambiente[param] = value
        # print(self.ambiente)

    def __load_sinais_vitais(self):
        sinais_vitais_file = open(self.sinais_vitais_path, "r")
        lines = sinais_vitais_file.readlines()
        sinais_vitais_file.close()
        for line in lines:
            self.sinais_vitais.append(
                [float(x) if i > 0 else int(x) for i, x in enumerate(line.replace('\n', '').replace(' ', '').split(','))])
        # print(self.sinais_vitais)

    def getMaxColumnas(self):
        return self.ambiente.get('XMax')

    def getMaxFilas(self):
        return self.ambiente.get('YMax')
