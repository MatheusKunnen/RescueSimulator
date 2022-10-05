from enum import Enum


class PosType(Enum):
    PAREDE = 1
    LIVRE = 2
    VITIMA = 3


ACTIONS = ["N", "S", "L", "O", "NE", "NO", "SE", "SO"]

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

ACTIONS_COST = {
    "N": 1.0,
    "S": 1.0,
    "L": 1.0,
    "O": 1.0,
    "NE": 1.5,
    "NO": 1.5,
    "SE": 1.5,
    "SO": 1.5,
    "A": 1.5,
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
