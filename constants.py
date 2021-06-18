import csv
import math

RNG = [177, 202, 238, 108, 90, 113, 46, 85, 214, 0, 204, 153, 144, 107, 125, 235, 79, 160, 7, 172, 223, 138, 86, 158,
       241, 154, 99, 117, 17, 145, 163, 184, 148, 115, 247, 84, 217, 110, 114, 192, 244, 128, 222, 185, 187, 141, 102,
       38, 208, 54, 225, 233, 112, 220, 205, 47, 74, 103, 93, 210, 96, 181, 157, 127, 69, 55, 80, 68, 120, 4, 25, 44,
       239, 253, 100, 129, 3, 218, 149, 76, 122, 11, 173, 31, 186, 221, 62, 249, 215, 26, 41, 248, 24, 179, 32, 246,
       209, 94, 52, 146, 123, 36, 67, 136, 151, 212, 15, 53, 170, 131, 104, 39, 168, 213, 190, 250, 20, 49, 175, 16, 13,
       216, 106, 206, 35, 97, 243, 61, 164, 8, 51, 227, 169, 56, 230, 147, 29, 28, 240, 14, 135, 89, 101, 130, 188, 255,
       254, 126, 143, 193, 30, 245, 203, 73, 2, 50, 9, 196, 142, 198, 43, 64, 167, 23, 118, 59, 22, 42, 200, 251, 178,
       88, 165, 21, 174, 37, 207, 70, 199, 72, 180, 10, 63, 201, 6, 133, 81, 137, 98, 77, 18, 140, 234, 162, 152, 75,
       121, 111, 92, 71, 48, 27, 231, 197, 34, 156, 232, 150, 58, 228, 124, 224, 105, 161, 183, 5, 57, 116, 1, 159, 189,
       195, 132, 252, 119, 134, 19, 78, 191, 242, 83, 91, 237, 33, 139, 109, 194, 65, 182, 219, 60, 211, 40, 236, 45,
       226, 155, 166, 66, 82, 87, 95, 229, 171, 176, 12]

# All offset values in order
OFFSET_TABLE = [0, 13, 26, 39, 52, 65, 78, 91, 104, 117, 130, 143, 156, 169, 182, 195, 208, 221, 234, 247, 4, 17, 30,
                43, 56, 69, 82, 95, 108, 121, 134, 147, 160, 173, 186, 199, 212, 225, 238, 251, 8, 21, 34, 47, 60, 73,
                86, 99, 112, 125, 138, 151, 164, 177, 190, 203, 216, 229, 242, 255, 12, 25, 38, 51, 64, 77, 90, 103,
                116, 129, 142, 155, 168, 181, 194, 207, 220, 233, 246, 3, 16, 29, 42, 55, 68, 81, 94, 107, 120, 133,
                146, 159, 172, 185, 198, 211, 224, 237, 250, 7, 20, 33, 46, 59, 72, 85, 98, 111, 124, 137, 150, 163,
                176, 189, 202, 215, 228, 241, 254, 11, 24, 37, 50, 63, 76, 89, 102, 115, 128, 141, 154, 167, 180, 193,
                206, 219, 232, 245, 2, 15, 28, 41, 54, 67, 80, 93, 106, 119, 132, 145, 158, 171, 184, 197, 210, 223,
                236, 249, 6, 19, 32, 45, 58, 71, 84, 97, 110, 123, 136, 149, 162, 175, 188, 201, 214, 227, 240, 253, 10,
                23, 36, 49, 62, 75, 88, 101, 114, 127, 140, 153, 166, 179, 192, 205, 218, 231, 244, 1, 14, 27, 40, 53,
                66, 79, 92, 105, 118, 131, 144, 157, 170, 183, 196, 209, 222, 235, 248, 5, 18, 31, 44, 57, 70, 83, 96,
                109, 122, 135, 148, 161, 174, 187, 200, 213, 226, 239, 252, 9, 22, 35, 48, 61, 74, 87, 100, 113, 126,
                139, 152, 165, 178, 191, 204, 217, 230, 243]

# The inverse of OFFSET_TABLE. INVERSE_OFFSET_TABLE[OFFSET_TABLE[x]] = x. Effectively stores the index of each offset value in OFFSET_TABLE.
INVERSE_OFFSET_TABLE = [0, 197, 138, 79, 20, 217, 158, 99, 40, 237, 178, 119, 60, 1, 198, 139, 80, 21, 218, 159, 100,
                        41, 238, 179, 120, 61, 2, 199, 140, 81, 22, 219, 160, 101, 42, 239, 180, 121, 62, 3, 200, 141,
                        82, 23, 220, 161, 102, 43, 240, 181, 122, 63, 4, 201, 142, 83, 24, 221, 162, 103, 44, 241, 182,
                        123, 64, 5, 202, 143, 84, 25, 222, 163, 104, 45, 242, 183, 124, 65, 6, 203, 144, 85, 26, 223,
                        164, 105, 46, 243, 184, 125, 66, 7, 204, 145, 86, 27, 224, 165, 106, 47, 244, 185, 126, 67, 8,
                        205, 146, 87, 28, 225, 166, 107, 48, 245, 186, 127, 68, 9, 206, 147, 88, 29, 226, 167, 108, 49,
                        246, 187, 128, 69, 10, 207, 148, 89, 30, 227, 168, 109, 50, 247, 188, 129, 70, 11, 208, 149, 90,
                        31, 228, 169, 110, 51, 248, 189, 130, 71, 12, 209, 150, 91, 32, 229, 170, 111, 52, 249, 190,
                        131, 72, 13, 210, 151, 92, 33, 230, 171, 112, 53, 250, 191, 132, 73, 14, 211, 152, 93, 34, 231,
                        172, 113, 54, 251, 192, 133, 74, 15, 212, 153, 94, 35, 232, 173, 114, 55, 252, 193, 134, 75, 16,
                        213, 154, 95, 36, 233, 174, 115, 56, 253, 194, 135, 76, 17, 214, 155, 96, 37, 234, 175, 116, 57,
                        254, 195, 136, 77, 18, 215, 156, 97, 38, 235, 176, 117, 58, 255, 196, 137, 78, 19, 216, 157, 98,
                        39, 236, 177, 118, 59]


class EncounterSlot:
    def __init__(self, formation: int, rate: int):
        self.formation = formation
        self.rate = rate

    def __eq__(self, other: "EncounterSlot"):
        return self.formation == other.formation and self.rate == other.rate


class EncounterTable:
    def __init__(self, rate: int, standard: list[EncounterSlot] = None, special: list[EncounterSlot] = None):
        self.rate = rate
        self.standard = standard
        self.special = special

    def __eq__(self, other: "EncounterTable"):
        return self.rate == other.rate and all([x[0] == x[1] for x in zip(self.standard, other.standard)]) and all(
            [x[0] == x[1] for x in zip(self.special, other.special)])


class Field:
    def __init__(self, field_id: int, field_name: str, table1: EncounterTable = None,
                 table2: EncounterTable = None):
        self.field_id = field_id
        self.field_name = field_name
        self.table1 = table1
        self.table2 = table2

    def __eq__(self, other: "Field"):
        return (self.field_id == other.field_id
                and self.field_name == other.field_name
                and self.table1 == other.table1
                and (
                        (self.table2 is None and other.table2 is None) or
                        (self.table2 is not None and other.table2 is not None)
                        and self.table2 == other.table2
                )
                )

    def encounter_on_formation(self, formation: int, preempt_rate: int = 16, table: int = 0):
        tbl = self.table1 if table == 1 or self.table2 is None else self.table2

        comparison_value = 0

        formation = (formation + 1) % 256
        fm_rng = RNG[formation] // 4
        # back attack 1
        if preempt_rate < 128:
            comparison_value += tbl.special[0].rate
        else:
            comparison_value += tbl.special[0].rate // 2
        if fm_rng < comparison_value:
            return tbl.special[0].formation, None, BATTLE_TYPE_NAMES[
                FORMATION_BATTLE_TYPE_MAP[tbl.special[0].formation]]
        # back attack 2
        if preempt_rate < 128:
            comparison_value += tbl.special[1].rate
        else:
            comparison_value += tbl.special[1].rate // 2
        if fm_rng < comparison_value:
            return tbl.special[1].formation, None, BATTLE_TYPE_NAMES[
                FORMATION_BATTLE_TYPE_MAP[tbl.special[1].formation]]
        # side attack
        comparison_value += tbl.special[2].rate
        if fm_rng < comparison_value:
            return tbl.special[2].formation, None, BATTLE_TYPE_NAMES[
                FORMATION_BATTLE_TYPE_MAP[tbl.special[2].formation]]
        # pincer
        if preempt_rate < 128:
            comparison_value += tbl.special[3].rate
        else:
            comparison_value += tbl.special[3].rate // 2
        if fm_rng < comparison_value:
            return tbl.special[3].formation, None, BATTLE_TYPE_NAMES[
                FORMATION_BATTLE_TYPE_MAP[tbl.special[3].formation]]

        # hardcoded exception for an encounter glitch
        if tbl.standard[0].rate > 32:
            return tbl.standard[0].formation, tbl.standard[0].formation, BATTLE_TYPE_NAMES[
                FORMATION_BATTLE_TYPE_MAP[tbl.standard[0].formation]]

        formation = (formation + 1) % 256
        fm_rng = RNG[formation] // 4
        comparison_value = 0

        encounter = tbl.standard[5].formation
        for i in range(5):
            comparison_value += tbl.standard[i].rate
            if fm_rng < comparison_value:
                encounter = tbl.standard[i].formation
                break

        formation2 = (formation + 1) % 256
        fm_rng = RNG[formation2] // 4
        comparison_value = 0

        for i in range(5):
            comparison_value += tbl.standard[i].rate
            if fm_rng < comparison_value:
                return encounter, tbl.standard[i].formation, BATTLE_TYPE_NAMES[
                    FORMATION_BATTLE_TYPE_MAP[tbl.standard[i].formation]]
        return encounter, tbl.standard[5].formation, BATTLE_TYPE_NAMES[
            FORMATION_BATTLE_TYPE_MAP[tbl.standard[5].formation]]


class Step:
    def __init__(self, step_id: int, offset: int):
        self.step_id = step_id
        self.offset = offset

    def __str__(self):
        return "(" + str(self.step_id) + ", " + str(self.offset) + ")"

    def __eq__(self, other: "Step"):
        return self.step_id == other.step_id and self.offset == other.offset

    def __add__(self, steps):
        if isinstance(steps, int):
            new_stepid = self.step_id + (2 * steps)
            return Step(new_stepid % 256,
                        OFFSET_TABLE[(INVERSE_OFFSET_TABLE[self.offset] + (new_stepid // 256)) % 256])

    def __sub__(self, other):
        if isinstance(other, int):
            return self.__add__(-other)
        elif isinstance(other, Step):
            return other.distance_to_step(self)

    def plus_steps(self, other: int):
        return self.__add__(other)

    # def advance_steps(self, steps: int):
    #     new_stepid = self.step_id + (2 * steps)
    #     self.offset = OFFSET_TABLE[(INVERSE_OFFSET_TABLE[self.offset] + (new_stepid // 256)) % 256]
    #     self.step_id = new_stepid % 256

    def distance_to_step(self, other: "Step"):
        return (((256 * (INVERSE_OFFSET_TABLE[other.offset] - INVERSE_OFFSET_TABLE[self.offset])) + (
                other.step_id - self.step_id)) // 2) % 32768

    # returns tuple: (danger threshold, is preemptive given current preempt rate, preemptive threshold)
    def encounter_threshold(self, lure_rate: int = 16, preempt_rate: int = 16):
        if lure_rate == 0:
            lure_rate = 1  # should never happen if the game is running, but it means it won't crash
        danger_threshold = (((RNG[self.step_id] - self.offset) % 256) + 1) * (4096 // lure_rate)
        step = self - 1
        preempt_threhsold = ((RNG[(step.step_id + 1) % 256] - step.offset) % 256)
        preempt = preempt_threhsold < (preempt_rate % 128)
        return danger_threshold, preempt, preempt_threhsold


class State:

    def field(self):
        if self.field_id in FIELDS:
            return FIELDS[self.field_id]
        return None

    def table(self):
        field = self.field()
        if field is not None:
            return field.table1 if self.table_index == 1 or field.table2 is None else field.table2
        return None

    def danger_increase_per_step_running(self):
        return (8 * self.danger_divisor_multipler) // self.table().rate

    def danger_increase_per_step_walking(self):
        return (2 * self.danger_divisor_multipler) // self.table().rate

    def next_encounter_data(self, start_step: Step = None, start_danger: int = None):
        if start_step is None:
            start_step = self.step
        if start_danger is None:
            start_danger = self.danger

        out = {}

        dips_run = self.danger_increase_per_step_running()
        dips_walk = self.danger_increase_per_step_walking()
        walking_steps = 0
        if dips_run - dips_walk == 0:  # prevent div by zero later if the game isn't set up properly
            return out
        while True:
            total_steps = walking_steps + 1
            danger = (start_danger + walking_steps * dips_walk) + dips_run
            while True:
                if danger >= (start_step + total_steps).encounter_threshold(self.lure_rate, self.preempt_rate)[0]:
                    out[walking_steps] = (start_step + walking_steps,
                                          start_danger + walking_steps * dips_walk), (
                                             start_step + total_steps, danger)
                    break
                danger += dips_run
                total_steps += 1
                if danger > 65536:
                    raise OverflowError("how")
            max_danger = (start_step + total_steps).encounter_threshold(self.lure_rate, self.preempt_rate)[0] - 1
            if max_danger < 0:
                break  # should never happen but who knows
            a = max_danger - (dips_run * total_steps)
            walking_steps = int(math.ceil((start_danger - a) / (dips_run - dips_walk)))
            if walking_steps > total_steps:
                out[-1] = (start_step, start_danger), (start_step + total_steps, start_danger + total_steps * dips_walk)
                return out

    def __init__(self, field_id: int, step: Step, formation_value: int = 0, step_fraction: int = 0, danger: int = 0,
                 table_index: int = 1, danger_divisor_multiplier: int = 512, lure_rate: int = 16,
                 preempt_rate: int = 16, last_encounter_formation: int = 0):
        self.field_id = field_id
        self.step = step
        self.step_fraction = step_fraction
        self.formation_value = formation_value
        self.danger = danger
        self.table_index = table_index
        self.danger_divisor_multipler = danger_divisor_multiplier
        self.lure_rate = lure_rate
        self.preempt_rate = preempt_rate
        self.last_encounter_formation = last_encounter_formation


FIELDS = dict()
NAME_ID_MAP = dict()
FORMATION_BATTLE_TYPE_MAP = dict()
FORMATION_PREEMPTABLE_MAP = dict()

BATTLE_TYPE_NAMES = ["Normal", "Side Attack", "Back Attack", "Pincer"]

with open("encdata.csv", "r") as f:
    _r = csv.reader(f)
    for _line in _r:
        _map_id = int(_line[46])
        _name = _line[47]
        _table1 = None
        _table2 = None
        if int(_line[0]) == 1:
            _standard = []
            for _i in range(6):
                _standard.append(EncounterSlot(int(_line[2 * _i + 0x2]), int(_line[2 * _i + 0x3])))
            _special = []
            for _i in range(4):
                _special.append(EncounterSlot(int(_line[2 * _i + 0xE]), int(_line[2 * _i + 0xF])))
            _table1 = EncounterTable(int(_line[1]), _standard, _special)
        if int(_line[24]) == 1:
            _standard = []
            for _i in range(6):
                _standard.append(EncounterSlot(int(_line[2 * _i + 0x18 + 0x2]), int(_line[2 * _i + 0x18 + 0x3])))
            _special = []
            for _i in range(4):
                _special.append(EncounterSlot(int(_line[2 * _i + 0x18 + 0xE]), int(_line[2 * _i + 0x18 + 0xF])))
            _table2 = EncounterTable(int(_line[1]), _standard, _special)
        FIELDS[_map_id] = Field(_map_id, _name, _table1, _table2)
        NAME_ID_MAP[_name] = _map_id

with open("formation.txt", "r") as f:
    for _line in f.readlines():
        _a = _line.split(" | ")[0].split(": ")
        FORMATION_BATTLE_TYPE_MAP[int(_a[0])] = int(_a[1])

with open("preemptive.txt", "r") as f:
    for _line in f.readlines():
        _a = _line.split(": ")
        FORMATION_PREEMPTABLE_MAP[int(_a[0])] = (int(_a[1]) == 1)

ENEMY_DATA = {
    "16": {
        "imgurl": "https://photos.app.goo.gl/uKa9B1uJe8TfV8ii8",
        "name": "MP"
    },
    "17": {
        "imgurl": "https://photos.app.goo.gl/hbyzDHVTBABBeaa1A",
        "name": "Guard Hound"
    },
    "18": {
        "imgurl": "https://photos.app.goo.gl/itqvjHUnUUutnuNUA",
        "name": "Mono Drive"
    },
    "19": {
        "imgurl": "https://photos.app.goo.gl/jZzmaXAaD9qciZgV7",
        "name": "Grunt"
    },
    "20": {
        "imgurl": "https://photos.app.goo.gl/kLjrjXGij6a9yHJ46",
        "name": "1st Ray"
    },
    "21": {
        "imgurl": "https://photos.app.goo.gl/NGHnS8barg4hBEsp8",
        "name": "Sweeper"
    },
    "23": {
        "imgurl": "https://photos.app.goo.gl/8kQdJpnhWLz59xgw6",
        "name": "Grashtrike"
    },
    "24": {
        "imgurl": "https://photos.app.goo.gl/4csDT9B5gV4vH2kZ6",
        "name": "Rocket Launcher"
    },
    "25": {
        "imgurl": "https://photos.app.goo.gl/aJW1pqBJULB2fWUSA",
        "name": "Whole Eater"
    },
    "26": {
        "imgurl": "https://photos.app.goo.gl/zLRfzioGduKuck2e7",
        "name": "Chuse Tank"
    },
    "27": {
        "imgurl": "https://photos.app.goo.gl/BuEbRe2NQkLdxBH38",
        "name": "Blugu"
    },
    "28": {
        "imgurl": "https://photos.app.goo.gl/J4vh2zxkJuLZ6xRQ8",
        "name": "Hedgehog Pie"
    },
    "29": {
        "imgurl": "https://photos.app.goo.gl/K5NBG9YPknm5jA4e7",
        "name": "Smogger"
    },
    "30": {
        "imgurl": "https://photos.app.goo.gl/Hu7zw7yMn5wxjG7M7",
        "name": "Special Combatant"
    },
    "31": {
        "imgurl": "https://photos.app.goo.gl/tfzpas5zrNGs7x1K7",
        "name": "Blood Taste"
    },
    "32": {
        "imgurl": "https://photos.app.goo.gl/hXCw21LuZHM2LtCA9",
        "name": "Proto Machinegun"
    },
    "34": {
        "imgurl": "https://photos.app.goo.gl/jppMLRgHLraPbTmY6",
        "name": "Vice"
    },
    "38": {
        "imgurl": "https://photos.app.goo.gl/Swa7o7ABTEsmaV7NA",
        "name": "Sahagin"
    },
    "39": {
        "imgurl": "https://photos.app.goo.gl/Cgfi3nYzFstN85Yu5",
        "name": "Ceasar"
    },
    "40": {
        "imgurl": "https://photos.app.goo.gl/YEUof3sdoAqw6HZg6",
        "name": "Eligor"
    },
    "41": {
        "imgurl": "https://photos.app.goo.gl/zaug27eVHf6LUR539",
        "name": "Ghost"
    },
    "42": {
        "imgurl": "https://photos.app.goo.gl/cqT7e9iYwVhAiq6P9",
        "name": "Cripshay"
    },
    "43": {
        "imgurl": "https://photos.app.goo.gl/eamdaGAuBgbKJeq26",
        "name": "Deenglow"
    },
    "44": {
        "imgurl": "https://photos.app.goo.gl/QckUqEeBP6sd8yXq7",
        "name": "Hell House"
    },
    "45": {
        "imgurl": "https://photos.app.goo.gl/gy5TFk4JvBAAeZYK6",
        "name": "Hell House"
    },
    "46": {
        "imgurl": "https://photos.app.goo.gl/MVkm8dimjSs9MZCK7",
        "name": "Aero Combatant"
    },
    "47": {
        "imgurl": "https://photos.app.goo.gl/SCKDQE2xD3Y3KeJi7",
        "name": "Aero Combatant"
    },
    "50": {
        "imgurl": "https://photos.app.goo.gl/pPZWVTjAUEFU7KRa9",
        "name": "Warning Board"
    },
    "51": {
        "imgurl": "https://photos.app.goo.gl/MFAKnAYv3Nu87UG86",
        "name": "Machine Gun"
    },
    "52": {
        "imgurl": "https://photos.app.goo.gl/8zGw33heaNb4xhwEA",
        "name": "Laser Cannon"
    },
    "53": {
        "imgurl": "https://photos.app.goo.gl/cyfCK1DKmQDJa8Nt9",
        "name": "Hammer Blaster"
    },
    "54": {
        "imgurl": "https://photos.app.goo.gl/oZQPR6uG17J4er2b8",
        "name": "[No Name]"
    },
    "55": {
        "imgurl": "https://photos.app.goo.gl/JoVaLkXeAz3SJuwx6",
        "name": "Sword Dance"
    },
    "56": {
        "imgurl": "https://photos.app.goo.gl/Mg63sTLyxoiF4ZdA6",
        "name": "SOLDIER:3rd"
    },
    "58": {
        "imgurl": "https://photos.app.goo.gl/fCrxq58TZF2nuKWV9",
        "name": "Mighty Grunt"
    },
    "59": {
        "imgurl": "https://photos.app.goo.gl/p2ix34rxkVim3YFA9",  # wrong
        "name": "Moth Slasher"
    },
    "60": {
        "imgurl": "https://photos.app.goo.gl/S6eScSKgRr4Gagod8",
        "name": "Grenade Combatant"
    },
    "61": {
        "imgurl": "https://photos.app.goo.gl/vaGH8PbYCWBXHLoc7",
        "name": "Brain Pod"
    },
    "62": {
        "imgurl": "https://photos.app.goo.gl/FKA6chYPTKbLtoB86",
        "name": "Vargid Police"
    },
    "63": {
        "imgurl": "https://photos.app.goo.gl/Hadu2AEC6tfQ3VZp6",
        "name": "Zenene"
    },
    "82": {
        "imgurl": "https://photos.app.goo.gl/VSY29RjZuZA5vWDS8",
        "name": "Madouge"
    },
    "83": {
        "imgurl": "https://photos.app.goo.gl/1SmFqEGGk8TQ8Jyv8",
        "name": "Crawler"
    },
    "84": {
        "imgurl": "https://photos.app.goo.gl/mUcDhkqXLfsnEsHu8",
        "name": "Ark Dragon"
    },
    "85": {
        "imgurl": "https://photos.app.goo.gl/XRbaXMYakUUaGJ3w7",
        "name": "Castanets"
    },
    "93": {
        "imgurl": "https://photos.app.goo.gl/FdvvwJx1aafLvBXe7",
        "name": "Scrutin Eye"
    },
    "94": {
        "imgurl": "https://photos.app.goo.gl/RmAVCU7KmjRs76V78",
        "name": "Marine"
    },
    "100": {
        "imgurl": "https://photos.app.goo.gl/K2yPLZftfSs8PWjg6",
        "name": "Search Crown"
    },
    "101": {
        "imgurl": "https://photos.app.goo.gl/FeWXGLdHwdPmzDmR7",
        "name": "Needle Kiss"
    },
    "102": {
        "imgurl": "https://photos.app.goo.gl/XRSELkJtiGtWCSbaA",
        "name": "Bloatfloat"
    },
    "103": {
        "imgurl": "https://photos.app.goo.gl/wttCpZkrSnDhhvyY6",
        "name": "Bagnadrana"
    },
    "104": {
        "imgurl": "https://photos.app.goo.gl/c5E5hkykEGnT5kLQ7",
        "name": "Cokatolis"
    },
    "105": {
        "imgurl": "https://photos.app.goo.gl/Wk6zpxCiBCeMrauw5",
        "name": "Bomb"
    },
    "106": {
        "imgurl": "https://photos.app.goo.gl/8pGgQiywubR5dWjR8",
        "name": "Death Claw"
    },
    "107": {
        "imgurl": "https://photos.app.goo.gl/VGhSaSypwEQeeqYQ7",
        "name": "2-Faced"
    },
    "108": {
        "imgurl": "https://photos.app.goo.gl/y9soGPjg9Wdccbwq6",
        "name": "Bandit"
    },
    "109": {
        "imgurl": "https://photos.app.goo.gl/h8fYqTjwNUPQuhv67",
        "name": "Bullmotor"
    },
    "110": {
        "imgurl": "https://photos.app.goo.gl/6qhQtN73BPaE4FuG6",
        "name": "Land Worm"
    },
    "119": {
        "imgurl": "https://photos.app.goo.gl/ka5HpoF4FK4wzAZ4A",
        "name": "Touch Me"
    },
    "121": {
        "imgurl": "https://photos.app.goo.gl/aAM7jXahG4nHGcxt9",
        "name": "Flower Prong"
    },
    "122": {
        "imgurl": "https://photos.app.goo.gl/8cR97j7UV5DCSqxJ6",
        "name": "Flower Prong"
    },
    "123": {
        "imgurl": "https://photos.app.goo.gl/kUdECpQB4s21mpAz8",
        "name": "Flower Prong"
    },
    "125": {
        "imgurl": "https://photos.app.goo.gl/Ssoknzeb2jeGyL5w8",
        "name": "Kimara Bug"
    },
    "126": {
        "imgurl": "https://photos.app.goo.gl/s49288TyzjZ3BQGHA",
        "name": "Heavy Tank"
    },
    "134": {
        "imgurl": "https://photos.app.goo.gl/GYR4MsDNnZVZKmLo6",
        "name": "Gi Spector"
    },
    "135": {
        "imgurl": "https://photos.app.goo.gl/jgjr5ZzB57vXVj759",
        "name": "Sneaky Step"
    },
    "136": {
        "imgurl": "https://photos.app.goo.gl/ZSEbTXfon19yuaiq9",
        "name": "Heg"
    },
    "145": {
        "imgurl": "https://photos.app.goo.gl/19SzRTuWexA7EMjM6",
        "name": "Mirage"
    },
    "146": {
        "imgurl": "https://photos.app.goo.gl/7QQNt7DCy53tN2zM8",
        "name": "Dorky Face"
    },
    "147": {
        "imgurl": "https://photos.app.goo.gl/Qf9xeVRZ4No7x8yj7",
        "name": "Jersey"
    },
    "148": {
        "imgurl": "https://photos.app.goo.gl/naHGoMjBpEjDwBgu9",
        "name": "Black Bat"
    },
    "149": {
        "imgurl": "https://photos.app.goo.gl/QBA6HZRAUX5FoHxt5",
        "name": "Ghirofelgo"
    },
    "150": {
        "imgurl": "https://photos.app.goo.gl/ZvEfpn6Vh5718q4p9",
        "name": "Chain"
    },
    "151": {
        "imgurl": "https://photos.app.goo.gl/bMs8KffPM21fdzxA9",
        "name": "Ying"
    },
    "152": {
        "imgurl": "https://photos.app.goo.gl/SBG9VzBzcRgb4ikC7",
        "name": "Yang"
    },
    "153": {
        "imgurl": "https://photos.app.goo.gl/eHTtjaKPKxvEkgit8",
        "name": "Beachplug"
    },
    "157": {
        "imgurl": "https://photos.app.goo.gl/BmnG7BnPCDDAWzWN6",
        "name": "Dragon"
    },
    "158": {
        "imgurl": "https://photos.app.goo.gl/DsZpTDhDvckKRTks5",
        "name": "Sonic Speed"
    },
    "159": {
        "imgurl": "https://photos.app.goo.gl/3moRSVXc11jm9FLWA",
        "name": "Twin Brain"
    },
    "160": {
        "imgurl": "https://photos.app.goo.gl/NnUvF4ksTEc27Eh18",
        "name": "Zuu"
    },
    "161": {
        "imgurl": "https://photos.app.goo.gl/wb2gcZi7QCm7ir7i6",
        "name": "Kyuvilduns"
    },
    "162": {
        "imgurl": "https://photos.app.goo.gl/dzmR5xrsBSijePHd8",
        "name": "Screamer"
    },
    "168": {
        "imgurl": "https://photos.app.goo.gl/4LehA6rZKKRzwAnb6",
        "name": "Razor Weed"
    },
    "170": {
        "imgurl": "https://photos.app.goo.gl/fDXYRSYgvKJ1vPTp7",
        "name": "Bizarre Bug"
    },
    "174": {
        "imgurl": "https://photos.app.goo.gl/7a8ccWJZpJrPpsM9A",
        "name": "Foulander"
    },
    "175": {
        "imgurl": "https://photos.app.goo.gl/CUu5Aeo62UZzVUfB6",
        "name": "Garuda"
    },
    "176": {
        "imgurl": "https://photos.app.goo.gl/5K8PfjvKi6YKHPTUA",
        "name": "Jayjujayme"
    },
    "185": {
        "imgurl": "https://photos.app.goo.gl/5zZATS74VgdWHfjU8",
        "name": "Under Lizard"
    },
    "186": {
        "imgurl": "https://photos.app.goo.gl/aMfnMw9Jee2EzNBo9",
        "name": "Kelzmelzer"
    },
    "189": {
        "imgurl": "https://photos.app.goo.gl/FKRh6X3DZRYqhKDz6",
        "name": "Toxic Frog"
    },
    "191": {
        "imgurl": "https://photos.app.goo.gl/JvrVK1HSPctmdduv6",
        "name": "Doorbull"
    },
    "192": {
        "imgurl": "https://photos.app.goo.gl/qxKYx2efQoJKQWUm7",
        "name": "Ancient Dragon"
    },
    "198": {
        "imgurl": "https://photos.app.goo.gl/VXAF5ZisU1P3wCQ98",
        "name": "Trickplay"
    },
    "199": {
        "imgurl": "https://photos.app.goo.gl/WyRXjTXajZVPCSK76",
        "name": "[No Name]"
    },
    "200": {
        "imgurl": "https://photos.app.goo.gl/nXGY4sDUvpKjzZ1X7",
        "name": "Boundfat"
    },
    "201": {
        "imgurl": "https://photos.app.goo.gl/iNEQ3V7DcMaYMzYUA",
        "name": "Malldancer"
    },
    "202": {
        "imgurl": "https://photos.app.goo.gl/yxRjvKLE8KjLNF9q9",
        "name": "Grimguard"
    },
    "203": {
        "imgurl": "https://photos.app.goo.gl/SkcoH5MuDN7Up5K5A",
        "name": "Hungry"
    },
    "204": {
        "imgurl": "https://photos.app.goo.gl/GWQt2eJATArwi69R8",
        "name": "Acrophies"
    },
    "205": {
        "imgurl": "https://photos.app.goo.gl/K4h9DRxf1dyFFGmm9",
        "name": "Ice Golem"
    },
    "206": {
        "imgurl": "https://photos.app.goo.gl/RW2d8Wu3MFH8Umfc6",
        "name": "Shred"
    },
    "207": {
        "imgurl": "https://photos.app.goo.gl/qAyXDLCy4ZiM6tsP7",
        "name": "Lessaloploth"
    },
    "208": {
        "imgurl": "https://photos.app.goo.gl/98rNsJrGNyyXGTjr7",
        "name": "Frozen Nail"
    },
    "210": {
        "imgurl": "https://photos.app.goo.gl/7znvTdDubXZsWHdA8",
        "name": "Snow"
    },
    "211": {
        "imgurl": "https://photos.app.goo.gl/HAvKRyxYT9H6EN2ZA",
        "name": "Bandersnatch"
    },
    "212": {
        "imgurl": "https://photos.app.goo.gl/teh3bHznXg5ktSUP8",
        "name": "Magnade"
    },
    "213": {
        "imgurl": "https://photos.app.goo.gl/3xfH4rbst9gfGyi69",
        "name": "[No Name]"
    },
    "214": {
        "imgurl": "https://photos.app.goo.gl/qCNTaR8thMFRtXbCA",
        "name": "[No Name]"
    },
    "215": {
        "imgurl": "https://photos.app.goo.gl/PsqZaoppadCoL5ZH6",
        "name": "Malboro"
    },
    "216": {
        "imgurl": "https://photos.app.goo.gl/4dNw4BFwfLRirmxM6",
        "name": "Blue Dragon"
    },
    "218": {
        "imgurl": "https://photos.app.goo.gl/TeGQ858svoz8iKV56",
        "name": "Headbomber"
    },
    "219": {
        "imgurl": "https://photos.app.goo.gl/WoH3PEG29dJ5wMyD7",
        "name": "Stilva"
    },
    "220": {
        "imgurl": "https://photos.app.goo.gl/8rUSvvT116pKYzEP7",
        "name": "Zolokalter"
    },
    "221": {
        "imgurl": "https://photos.app.goo.gl/RZETPJp7EUYpfb989",
        "name": "Evilhead"
    },
    "222": {
        "imgurl": "https://photos.app.goo.gl/SnbsGU1mPL8FHLs39",
        "name": "Cuahl"
    },
    "223": {
        "imgurl": "https://photos.app.goo.gl/QN7UGT2M94VrnHo49",
        "name": "Gigas"
    },
    "224": {
        "imgurl": "https://photos.app.goo.gl/TnZnKZn6XQ9JpkVM8",
        "name": "Grenade"
    },
    "225": {
        "imgurl": "https://photos.app.goo.gl/dTWc6UgrwRXRzCTD8",
        "name": "Gremlin"
    },
    "226": {
        "imgurl": "https://photos.app.goo.gl/CSjrr6a64n7rzEx49",
        "name": "Ironite"
    },
    "227": {
        "imgurl": "https://photos.app.goo.gl/GahLQEvkaZm4jmUH7",
        "name": "Sculpture"
    },
    "230": {
        "imgurl": "https://photos.app.goo.gl/5jJHgxzyhPyEeCve6",
        "name": "Wind Wing"
    },
    "231": {
        "imgurl": "https://photos.app.goo.gl/CjM2T8oP5KkrDX7m8",
        "name": "Dragon Rider"
    },
    "232": {
        "imgurl": "https://photos.app.goo.gl/9KGjdnQESym97R7K8",
        "name": "Killbin"
    },
    "233": {
        "imgurl": "https://photos.app.goo.gl/VfrNrJu3KAG3CcxRA",
        "name": "Tonberry"
    },
    "235": {
        "imgurl": "https://photos.app.goo.gl/MMtXcmaYUwZnoqGL9",
        "name": "Roulette Cannon"
    },
    "236": {
        "imgurl": "https://photos.app.goo.gl/ujwYsqS2hChWBTPQ7",
        "name": "Pedestal"
    },
    "237": {
        "imgurl": "https://photos.app.goo.gl/i8FRmQgE1j8qyZyX6",
        "name": "SOLDIER:2nd"
    },
    "238": {
        "imgurl": "https://photos.app.goo.gl/yaRYhc8S4Z21knqj9",
        "name": "Death Machine"
    },
    "239": {
        "imgurl": "https://photos.app.goo.gl/GksNwTTKeq4ZNXw46",
        "name": "Slalom"
    },
    "240": {
        "imgurl": "https://photos.app.goo.gl/KXB6D5k87auuD9Xm9",
        "name": "Scissors"
    },
    "241": {
        "imgurl": "https://photos.app.goo.gl/7kLE1AJVTKFv1NP99",
        "name": "Scissors(Upper)"
    },
    "242": {
        "imgurl": "https://photos.app.goo.gl/pBy2PD9CFbBxGBCy6",
        "name": "Scissors(Lower)"
    },
    "243": {
        "imgurl": "https://photos.app.goo.gl/ru9YST91V9ToC2EM9",
        "name": "Guard System"
    },
    "244": {
        "imgurl": "https://photos.app.goo.gl/E6NYsUJDQdRfUciYA",
        "name": "Quick Machine Gun"
    },
    "245": {
        "imgurl": "https://photos.app.goo.gl/B3CVdSYrAYaJgwQV6",
        "name": "Rocket Launcher"
    },
    "246": {
        "imgurl": "https://photos.app.goo.gl/FQsWzuz42dPRL6BH9",
        "name": "Ghost Ship"
    },
    "247": {
        "imgurl": "https://photos.app.goo.gl/jQwrbjGaK64rT42J6",
        "name": "Corvette"
    },
    "248": {
        "imgurl": "https://photos.app.goo.gl/raykHvkT8BtUm8Xd8",
        "name": "Diver Nest"
    },
    "252": {
        "imgurl": "https://photos.app.goo.gl/QSmQf21i7DcUxxSi6",
        "name": "Senior Grunt"
    },
    "253": {
        "imgurl": "https://photos.app.goo.gl/ESWDZ9GB6QXGfoZMA",
        "name": "Hard Attacker"
    },
    "254": {
        "imgurl": "https://photos.app.goo.gl/1robspgofYDwCsNy6",
        "name": "Guardian"
    },
    "255": {
        "imgurl": "https://photos.app.goo.gl/gf6t2mLaEEt6p4mw7",
        "name": "Guardian(Right)"
    },
    "257": {
        "imgurl": "https://photos.app.goo.gl/vrvRs1g6HSzhKTd86",
        "name": "Gun Carrier"
    },
    "261": {
        "imgurl": "https://photos.app.goo.gl/NQeCmPRY1GoiZtjf8",
        "name": "Rilfsak"
    },
    "262": {
        "imgurl": "https://photos.app.goo.gl/QbCye2augFM9wprU9",
        "name": "Diablo"
    },
    "263": {
        "imgurl": "https://photos.app.goo.gl/yAh2ECUqChcpktaz5",
        "name": "Epiolnis"
    },
    "268": {
        "imgurl": "https://photos.app.goo.gl/sRuXaEg9QzavCNdC7",
        "name": "Serpent"
    },
    "269": {
        "imgurl": "https://photos.app.goo.gl/rxVcm5j1NtAHcVie8",
        "name": "Poodler"
    },
    "270": {
        "imgurl": "https://photos.app.goo.gl/KvqWSDaiTK1eqnxX9",
        "name": "Bad Rap"
    },
    "271": {
        "imgurl": "https://photos.app.goo.gl/MHoySUyTMQBV9KRK8",
        "name": "Unknown"
    },
    "272": {
        "imgurl": "https://photos.app.goo.gl/ePyvguuGH5qZjjPb9",
        "name": "Unknown 3"
    },
    "273": {
        "imgurl": "https://photos.app.goo.gl/HNSMUy5k9eiYQozT6",
        "name": "Unknown 2"
    },
    "285": {
        "imgurl": "https://photos.app.goo.gl/8D7khA9dZPHVQQHB6",
        "name": "Behemoth"
    },
    "286": {
        "imgurl": "https://photos.app.goo.gl/iS2U3sm5ajsCPXHT7",
        "name": "Cromwell"
    },
    "287": {
        "imgurl": "https://photos.app.goo.gl/5H2wogrVL1WB62cc8",
        "name": "Manhole"
    },
    "288": {
        "imgurl": "https://photos.app.goo.gl/Vjs9ZzhFE9PWzpvu6",
        "name": "Manhole(Lid)"
    },
    "289": {
        "imgurl": "https://photos.app.goo.gl/iHM5zuCUg45yy1tx5",
        "name": "Crazy Saw"
    },
    "290": {
        "imgurl": "https://photos.app.goo.gl/fsDq5q5bw1FnZ3XH6",
        "name": "Shadow Maker"
    },
    "291": {
        "imgurl": "https://photos.app.goo.gl/9bjZci2gXmy8ZQk46",
        "name": "Grosspanzer-Big"
    },
    "292": {
        "imgurl": "https://photos.app.goo.gl/11ziyGG3UxGdkpBn6",
        "name": "Grosspanzer-Small"
    },
    "293": {
        "imgurl": "https://photos.app.goo.gl/xrrwxXQm3p3CqKrh6",
        "name": "Grosspanzer-Mobile"
    },
    "294": {
        "imgurl": "https://photos.app.goo.gl/4AGEXWtJst5UX3Yn9",
        "name": "Gargoyle"
    },
    "295": {
        "imgurl": "https://photos.app.goo.gl/HhrXPuCWnknU3SB7A",
        "name": "Gargoyle"
    },
    "301": {
        "imgurl": "https://photos.app.goo.gl/sPKZEj8az5MMA1hHA",
        "name": "SOLDIER:1st"
    },
    "302": {
        "imgurl": "https://photos.app.goo.gl/1aFEqW2USvstB7Tw7",
        "name": "XCannon"
    },
    "304": {
        "imgurl": "https://photos.app.goo.gl/PqVVvBPRsvMZS8qB8",
        "name": "Maximum Kimaira"
    },
    "310": {
        "imgurl": "https://photos.app.goo.gl/va4AmqL3TyXHbQSY9",
        "name": "Magic Pot"
    },
    "311": {
        "imgurl": "https://photos.app.goo.gl/X7MFeSCKFTs4haw58",
        "name": "Christopher"
    },
    "312": {
        "imgurl": "https://photos.app.goo.gl/XWbQ31hyDioBm27WA",
        "name": "Gighee"
    },
    "313": {
        "imgurl": "https://photos.app.goo.gl/quQcJFHf6urGS5iTA",
        "name": "King Behemoth"
    },
    "314": {
        "imgurl": "https://photos.app.goo.gl/xNTn8ZKwYrc8cU95A",
        "name": "Allemagne"
    },
    "315": {
        "imgurl": "https://photos.app.goo.gl/jMWC6aJad1gnmQdS9",
        "name": "Dragon Zombie"
    },
    "316": {
        "imgurl": "https://photos.app.goo.gl/zopxFNqcVH2YXvse6",
        "name": "Armored Golem"
    },
    "317": {
        "imgurl": "https://photos.app.goo.gl/BspDbAvVQ15kxH7R6",
        "name": "Master Tonberry"
    },
    "318": {
        "imgurl": "https://photos.app.goo.gl/YEb7So4fB6Qd9k9JA",
        "name": "Pollensalta"
    },
    "319": {
        "imgurl": "https://photos.app.goo.gl/UE6759rCGVqzSRG78",
        "name": "Mover"
    },
    "321": {
        "imgurl": "https://photos.app.goo.gl/jhs56RjwPZL5Cdvj6",
        "name": "Parasite"
    },
    "322": {
        "imgurl": "https://photos.app.goo.gl/ZizgR5jtNG9Zcaj56",
        "name": "Dark Dragon"
    },
    "323": {
        "imgurl": "https://photos.app.goo.gl/y7YeysfFQ48AAAH16",
        "name": "Death Dealer"
    },
    "364": {
        "imgurl": "https://photos.app.goo.gl/A5GgMLsMCDiC642D7",
        "name": "Cactuar"
    }
}

ENCOUNTER_DATA = {
    "256": {
        "battle_type": 0,
        "enemies": [
            364
        ]
    },
    "301": {
        "battle_type": 0,
        "enemies": [
            16,
            16
        ]
    },
    "302": {
        "battle_type": 0,
        "enemies": [
            17
        ]
    },
    "303": {
        "battle_type": 0,
        "enemies": [
            16,
            17
        ]
    },
    "304": {
        "battle_type": 2,
        "enemies": [
            17
        ]
    },
    "305": {
        "battle_type": 0,
        "enemies": [
            18,
            18
        ]
    },
    "306": {
        "battle_type": 0,
        "enemies": [
            16,
            16,
            18
        ]
    },
    "307": {
        "battle_type": 0,
        "enemies": [
            16,
            16
        ]
    },
    "308": {
        "battle_type": 0,
        "enemies": [
            18,
            18,
            20
        ]
    },
    "309": {
        "battle_type": 0,
        "enemies": [
            20,
            20
        ]
    },
    "310": {
        "battle_type": 0,
        "enemies": [
            19,
            19
        ]
    },
    "311": {
        "battle_type": 0,
        "enemies": [
            20,
            19,
            20
        ]
    },
    "312": {
        "battle_type": 0,
        "enemies": [
            20,
            20,
            20
        ]
    },
    "313": {
        "battle_type": 0,
        "enemies": [
            19,
            19,
            19
        ]
    },
    "314": {
        "battle_type": 2,
        "enemies": [
            18,
            18
        ]
    },
    "315": {
        "battle_type": 2,
        "enemies": [
            19,
            19,
            19
        ]
    },
    "316": {
        "battle_type": 0,
        "enemies": [
            19,
            19,
            18,
            18
        ]
    },
    "317": {
        "battle_type": 0,
        "enemies": [
            19,
            19,
            18,
            18,
            18
        ]
    },
    "318": {
        "battle_type": 0,
        "enemies": [
            19,
            19,
            19
        ]
    },
    "319": {
        "battle_type": 2,
        "enemies": [
            19,
            19,
            18
        ]
    },
    "320": {
        "battle_type": 0,
        "enemies": [
            21
        ]
    },
    "321": {
        "battle_type": 0,
        "enemies": [
            21,
            19,
            19
        ]
    },
    "322": {
        "battle_type": 0,
        "enemies": [
            19,
            19,
            21
        ]
    },
    "323": {
        "battle_type": 2,
        "enemies": [
            19,
            19
        ]
    },
    "332": {
        "battle_type": 0,
        "enemies": [
            24,
            24,
            24,
            24
        ]
    },
    "333": {
        "battle_type": 0,
        "enemies": [
            23,
            23,
            23
        ]
    },
    "334": {
        "battle_type": 0,
        "enemies": [
            23,
            23,
            23,
            23
        ]
    },
    "335": {
        "battle_type": 2,
        "enemies": [
            23,
            23,
            23,
            23
        ]
    },
    "336": {
        "battle_type": 0,
        "enemies": [
            23,
            23,
            26,
            26
        ]
    },
    "337": {
        "battle_type": 0,
        "enemies": [
            26,
            26,
            26
        ]
    },
    "338": {
        "battle_type": 0,
        "enemies": [
            26,
            26,
            26,
            23,
            23
        ]
    },
    "340": {
        "battle_type": 0,
        "enemies": [
            24,
            24,
            24
        ]
    },
    "341": {
        "battle_type": 0,
        "enemies": [
            24,
            24,
            27,
            27
        ]
    },
    "342": {
        "battle_type": 0,
        "enemies": [
            24,
            27,
            27
        ]
    },
    "343": {
        "battle_type": 2,
        "enemies": [
            26,
            27,
            27,
            27
        ]
    },
    "344": {
        "battle_type": 0,
        "enemies": [
            30,
            30,
            30
        ]
    },
    "345": {
        "battle_type": 0,
        "enemies": [
            32,
            32,
            32
        ]
    },
    "346": {
        "battle_type": 0,
        "enemies": [
            32,
            32,
            30,
            30
        ]
    },
    "347": {
        "battle_type": 0,
        "enemies": [
            31,
            31,
            30,
            30
        ]
    },
    "348": {
        "battle_type": 0,
        "enemies": [
            31,
            31,
            31,
            31
        ]
    },
    "349": {
        "battle_type": 2,
        "enemies": [
            30,
            30,
            32
        ]
    },
    "350": {
        "battle_type": 2,
        "enemies": [
            31,
            31,
            31
        ]
    },
    "352": {
        "battle_type": 0,
        "enemies": [
            30,
            29,
            29
        ]
    },
    "353": {
        "battle_type": 0,
        "enemies": [
            29,
            29,
            32
        ]
    },
    "354": {
        "battle_type": 0,
        "enemies": [
            30,
            30,
            30,
            30
        ]
    },
    "355": {
        "battle_type": 0,
        "enemies": [
            29,
            29
        ]
    },
    "356": {
        "battle_type": 0,
        "enemies": [
            32,
            32,
            32,
            32,
            32
        ]
    },
    "357": {
        "battle_type": 0,
        "enemies": [
            29,
            29,
            31
        ]
    },
    "358": {
        "battle_type": 0,
        "enemies": [
            29,
            31,
            31
        ]
    },
    "359": {
        "battle_type": 2,
        "enemies": [
            31,
            31,
            31
        ]
    },
    "368": {
        "battle_type": 0,
        "enemies": [
            28,
            28,
            28
        ]
    },
    "369": {
        "battle_type": 0,
        "enemies": [
            28,
            28
        ]
    },
    "370": {
        "battle_type": 2,
        "enemies": [
            28,
            28
        ]
    },
    "376": {
        "battle_type": 0,
        "enemies": [
            25,
            25
        ]
    },
    "377": {
        "battle_type": 0,
        "enemies": [
            25,
            28,
            28
        ]
    },
    "378": {
        "battle_type": 0,
        "enemies": [
            34,
            34
        ]
    },
    "379": {
        "battle_type": 2,
        "enemies": [
            34
        ]
    },
    "380": {
        "battle_type": 0,
        "enemies": [
            44
        ]
    },
    "381": {
        "battle_type": 0,
        "enemies": [
            25,
            25,
            25,
            25
        ]
    },
    "382": {
        "battle_type": 2,
        "enemies": {
            44
        }
    },
    "388": {
        "battle_type": 0,
        "enemies": [
            39,
            39,
            39
        ]
    },
    "389": {
        "battle_type": 0,
        "enemies": [
            38,
            38,
            39
        ]
    },
    "390": {
        "battle_type": 0,
        "enemies": [
            38,
            38
        ]
    },
    "391": {
        "battle_type": 0,
        "enemies": [
            38,
            38,
            38
        ]
    },
    "392": {
        "battle_type": 0,
        "enemies": [
            18,
            18,
            18
        ]
    },
    "393": {
        "battle_type": 0,
        "enemies": [
            17,
            17
        ]
    },
    "394": {
        "battle_type": 0,
        "enemies": [
            18,
            18,
            18
        ]
    },
    "395": {
        "battle_type": 0,
        "enemies": [
            21
        ]
    },
    "396": {
        "battle_type": 0,
        "enemies": [
            42,
            42,
            43
        ]
    },
    "397": {
        "battle_type": 0,
        "enemies": [
            43,
            43
        ]
    },
    "398": {
        "battle_type": 0,
        "enemies": [
            41,
            41,
            41
        ]
    },
    "399": {
        "battle_type": 0,
        "enemies": [
            41,
            43,
            41
        ]
    },
    "400": {
        "battle_type": 0,
        "enemies": [
            40
        ]
    },
    "401": {
        "battle_type": 0,
        "enemies": [
            43,
            43,
            43
        ]
    },
    "404": {
        "battle_type": 0,
        "enemies": [
            46,
            47,
            46,
            47
        ]
    },
    "405": {
        "battle_type": 0,
        "enemies": [
            46,
            47,
            46,
            47,
            46,
            47
        ]
    },
    "406": {
        "battle_type": 0,
        "enemies": [
            46,
            47
        ]
    },
    "407": {
        "battle_type": 2,
        "enemies": [
            46,
            47,
            46,
            47
        ]
    },
    "416": {
        "battle_type": 0,
        "enemies": [
            60,
            60
        ]
    },
    "417": {
        "battle_type": 0,
        "enemies": [
            60,
            60,
            60
        ]
    },
    "419": {
        "battle_type": 0,
        "enemies": [
            59
        ]
    },
    "420": {
        "battle_type": 0,
        "enemies": [
            59,
            59
        ]
    },
    "421": {
        "battle_type": 0,
        "enemies": [
            59,
            59,
            59
        ]
    },
    "424": {
        "battle_type": 0,
        "enemies": [
            53
        ]
    },
    "425": {
        "battle_type": 0,
        "enemies": [
            55
        ]
    },
    "426": {
        "battle_type": 0,
        "enemies": [
            53,
            53
        ]
    },
    "427": {
        "battle_type": 0,
        "enemies": [
            55,
            55
        ]
    },
    "428": {
        "battle_type": 0,
        "enemies": [
            55,
            55,
            55
        ]
    },
    "429": {
        "battle_type": 2,
        "enemies": [
            53,
            53
        ]
    },
    "432": {
        "battle_type": 0,
        "enemies": [
            50
        ]
    },
    "433": {
        "battle_type": 0,
        "enemies": [
            50,
            50
        ]
    },
    "436": {
        "battle_type": 0,
        "enemies": [
            59
        ]
    },
    "437": {
        "battle_type": 0,
        "enemies": [
            56,
            56
        ]
    },
    "438": {
        "battle_type": 0,
        "enemies": [
            59,
            59
        ]
    },
    "439": {
        "battle_type": 2,
        "enemies": [
            59
        ]
    },
    "440": {
        "battle_type": 0,
        "enemies": [
            56,
            56,
            56
        ]
    },
    "441": {
        "battle_type": 0,
        "enemies": [
            59,
            59,
            59
        ]
    },
    "442": {
        "battle_type": 0,
        "enemies": [
            59,
            56,
            56
        ]
    },
    "443": {
        "battle_type": 2,
        "enemies": [
            56,
            56
        ]
    },
    "444": {
        "battle_type": 0,
        "enemies": [
            61,
            61
        ]
    },
    "445": {
        "battle_type": 0,
        "enemies": [
            61
        ]
    },
    "446": {
        "battle_type": 0,
        "enemies": [
            62,
            62,
            62
        ]
    },
    "447": {
        "battle_type": 2,
        "enemies": [
            61,
            62,
            62
        ]
    },
    "448": {
        "battle_type": 0,
        "enemies": [
            63,
            63
        ]
    },
    "449": {
        "battle_type": 0,
        "enemies": [
            62,
            63
        ]
    },
    "450": {
        "battle_type": 0,
        "enemies": [
            61,
            61,
            63
        ]
    },
    "452": {
        "battle_type": 0,
        "enemies": [
            63
        ]
    },
    "453": {
        "battle_type": 0,
        "enemies": [
            62,
            62
        ]
    },
    "454": {
        "battle_type": 2,
        "enemies": [
            63,
            63
        ]
    },
    "472": {
        "battle_type": 0,
        "enemies": [
            82,
            82
        ]
    },
    "473": {
        "battle_type": 0,
        "enemies": [
            82,
            83,
            83,
            82,
            83
        ]
    },
    "474": {
        "battle_type": 0,
        "enemies": [
            85,
            85,
            85
        ]
    },
    "475": {
        "battle_type": 2,
        "enemies": [
            83,
            83,
            83,
            83
        ]
    },
    "476": {
        "battle_type": 0,
        "enemies": [
            83,
            83,
            83,
            84
        ]
    },
    "477": {
        "battle_type": 0,
        "enemies": [
            85,
            85,
            85,
            85
        ]
    },
    "478": {
        "battle_type": 0,
        "enemies": [
            85,
            85,
            84,
            83
        ]
    },
    "479": {
        "battle_type": 0,
        "enemies": [
            83,
            83,
            83,
            83,
            83
        ]
    },
    "484": {
        "battle_type": 0,
        "enemies": [
            93,
            93,
            93,
            93
        ]
    },
    "485": {
        "battle_type": 0,
        "enemies": [
            94,
            94
        ]
    },
    "486": {
        "battle_type": 0,
        "enemies": [
            94,
            94,
            94
        ]
    },
    "487": {
        "battle_type": 2,
        "enemies": [
            93,
            93,
            93,
            93
        ]
    },
    "492": {
        "battle_type": 0,
        "enemies": [
            101,
            101,
            101
        ]
    },
    "493": {
        "battle_type": 0,
        "enemies": [
            100,
            100,
            100,
            101
        ]
    },
    "494": {
        "battle_type": 0,
        "enemies": [
            101,
            100,
            103
        ]
    },
    "495": {
        "battle_type": 2,
        "enemies": [
            101,
            101,
            101
        ]
    },
    "496": {
        "battle_type": 0,
        "enemies": [
            102,
            102,
            102
        ]
    },
    "497": {
        "battle_type": 0,
        "enemies": [
            103,
            103
        ]
    },
    "498": {
        "battle_type": 0,
        "enemies": [
            102,
            102,
            102,
            102
        ]
    },
    "499": {
        "battle_type": 0,
        "enemies": [
            102,
            103,
            102
        ]
    },
    "500": {
        "battle_type": 0,
        "enemies": [
            105
        ]
    },
    "501": {
        "battle_type": 0,
        "enemies": [
            105,
            105
        ]
    },
    "502": {
        "battle_type": 0,
        "enemies": [
            104,
            102,
            102
        ]
    },
    "503": {
        "battle_type": 0,
        "enemies": [
            104,
            104
        ]
    },
    "504": {
        "battle_type": 0,
        "enemies": [
            101,
            101,
            101,
            104
        ]
    },
    "505": {
        "battle_type": 0,
        "enemies": [
            104,
            104
        ]
    },
    "506": {
        "battle_type": 2,
        "enemies": [
            104
        ]
    },
    "508": {
        "battle_type": 0,
        "enemies": [
            100,
            100,
            100,
            100,
            100
        ]
    },
    "509": {
        "battle_type": 0,
        "enemies": [
            101,
            101,
            103
        ]
    },
    "510": {
        "battle_type": 0,
        "enemies": [
            100,
            100,
            100,
            101,
            101
        ]
    },
    "513": {
        "battle_type": 0,
        "enemies": [
            105
        ]
    },
    "514": {
        "battle_type": 0,
        "enemies": [
            103
        ]
    },
    "516": {
        "battle_type": 0,
        "enemies": [
            107,
            108,
            108
        ]
    },
    "517": {
        "battle_type": 0,
        "enemies": [
            107,
            107,
            108
        ]
    },
    "518": {
        "battle_type": 0,
        "enemies": [
            107,
            107,
            107
        ]
    },
    "520": {
        "battle_type": 2,
        "enemies": [
            107,
            107,
            107,
            107
        ]
    },
    "521": {
        "battle_type": 0,
        "enemies": [
            106,
            106
        ]
    },
    "522": {
        "battle_type": 0,
        "enemies": [
            109,
            109,
            109,
            109
        ]
    },
    "523": {
        "battle_type": 0,
        "enemies": [
            106,
            106,
            109
        ]
    },
    "524": {
        "battle_type": 0,
        "enemies": [
            110
        ]
    },
    "528": {
        "battle_type": 0,
        "enemies": [
            125
        ]
    },
    "529": {
        "battle_type": 0,
        "enemies": [
            119
        ]
    },
    "530": {
        "battle_type": 0,
        "enemies": [
            125,
            125
        ]
    },
    "532": {
        "battle_type": 0,
        "enemies": [
            121,
            122,
            123
        ]
    },
    "536": {
        "battle_type": 0,
        "enemies": [
            126
        ]
    },
    "537": {
        "battle_type": 2,
        "enemies": [
            126
        ]
    },
    "540": {
        "battle_type": 0,
        "enemies": [
            136,
            136,
            136,
            136
        ]
    },
    "541": {
        "battle_type": 0,
        "enemies": [
            135
        ]
    },
    "542": {
        "battle_type": 0,
        "enemies": [
            136,
            136,
            135
        ]
    },
    "543": {
        "battle_type": 0,
        "enemies": [
            135,
            135,
            135
        ]
    },
    "544": {
        "battle_type": 0,
        "enemies": [
            135,
            135
        ]
    },
    "545": {
        "battle_type": 0,
        "enemies": [
            136,
            136,
            136,
            136,
            136
        ]
    },
    "546": {
        "battle_type": 2,
        "enemies": [
            135,
            135
        ]
    },
    "547": {
        "battle_type": 0,
        "enemies": [
            134
        ]
    },
    "548": {
        "battle_type": 0,
        "enemies": [
            135,
            136,
            136,
            136
        ]
    },
    "549": {
        "battle_type": 1,
        "enemies": [
            135,
            135
        ]
    },
    "552": {
        "battle_type": 2,
        "enemies": [
            134,
            134
        ]
    },
    "556": {
        "battle_type": 0,
        "enemies": [
            146,
            146,
            146
        ]
    },
    "557": {
        "battle_type": 0,
        "enemies": [
            146,
            146,
            146,
            146
        ]
    },
    "558": {
        "battle_type": 0,
        "enemies": [
            149,
            150
        ]
    },
    "559": {
        "battle_type": 2,
        "enemies": [
            149,
            150
        ]
    },
    "560": {
        "battle_type": 0,
        "enemies": [
            146,
            146,
            146,
            146
        ]
    },
    "561": {
        "battle_type": 0,
        "enemies": [
            145,
            145,
            146
        ]
    },
    "562": {
        "battle_type": 0,
        "enemies": [
            147,
            147,
            147
        ]
    },
    "564": {
        "battle_type": 0,
        "enemies": [
            146,
            146,
            148
        ]
    },
    "565": {
        "battle_type": 0,
        "enemies": [
            146,
            146,
            145
        ]
    },
    "566": {
        "battle_type": 2,
        "enemies": [
            148,
            148,
            148
        ]
    },
    "567": {
        "battle_type": 0,
        "enemies": [
            148,
            148
        ]
    },
    "568": {
        "battle_type": 0,
        "enemies": [
            148,
            148,
            148
        ]
    },
    "569": {
        "battle_type": 0,
        "enemies": [
            148,
            148,
            148,
            148
        ]
    },
    "570": {
        "battle_type": 2,
        "enemies": [
            148,
            148,
            148
        ]
    },
    "572": {
        "battle_type": 0,
        "enemies": [
            151,
            152,
            153
        ]
    },
    "573": {
        "battle_type": 0,
        "enemies": [
            151,
            152,
            153
        ]
    },
    "574": {
        "battle_type": 2,
        "enemies": [
            151,
            152,
            153
        ]
    },
    "580": {
        "battle_type": 0,
        "enemies": [
            161,
            161
        ]
    },
    "581": {
        "battle_type": 0,
        "enemies": [
            161,
            161,
            161
        ]
    },
    "582": {
        "battle_type": 0,
        "enemies": [
            158,
            161,
            161
        ]
    },
    "583": {
        "battle_type": 0,
        "enemies": [
            158,
            158
        ]
    },
    "584": {
        "battle_type": 0,
        "enemies": [
            158,
            158,
            158
        ]
    },
    "585": {
        "battle_type": 0,
        "enemies": [
            158,
            158
        ]
    },
    "586": {
        "battle_type": 0,
        "enemies": [
            160
        ]
    },
    "588": {
        "battle_type": 0,
        "enemies": [
            159,
            159,
            158
        ]
    },
    "589": {
        "battle_type": 0,
        "enemies": [
            159,
            159,
            159
        ]
    },
    "590": {
        "battle_type": 0,
        "enemies": [
            158,
            158,
            158
        ]
    },
    "591": {
        "battle_type": 0,
        "enemies": [
            160
        ]
    },
    "592": {
        "battle_type": 0,
        "enemies": [
            162,
            159,
            162
        ]
    },
    "593": {
        "battle_type": 2,
        "enemies": [
            162,
            162
        ]
    },
    "596": {
        "battle_type": 0,
        "enemies": [
            161,
            161,
            161,
            161,
            161
        ]
    },
    "597": {
        "battle_type": 0,
        "enemies": [
            159,
            159,
            159
        ]
    },
    "598": {
        "battle_type": 0,
        "enemies": [
            159,
            159,
            161,
            161,
            161
        ]
    },
    "599": {
        "battle_type": 0,
        "enemies": [
            157
        ]
    },
    "604": {
        "battle_type": 0,
        "enemies": [
            168,
            168,
            168
        ]
    },
    "605": {
        "battle_type": 0,
        "enemies": [
            170,
            170
        ]
    },
    "606": {
        "battle_type": 0,
        "enemies": [
            176,
            176,
            170
        ]
    },
    "607": {
        "battle_type": 2,
        "enemies": [
            168,
            168,
            168
        ]
    },
    "608": {
        "battle_type": 0,
        "enemies": [
            174,
            170,
            170,
            170
        ]
    },
    "609": {
        "battle_type": 0,
        "enemies": [
            174,
            174
        ]
    },
    "610": {
        "battle_type": 0,
        "enemies": [
            174,
            174,
            174
        ]
    },
    "611": {
        "battle_type": 2,
        "enemies": [
            174,
            174
        ]
    },
    "612": {
        "battle_type": 0,
        "enemies": [
            176,
            176,
            176,
            175
        ]
    },
    "613": {
        "battle_type": 0,
        "enemies": [
            175,
            175
        ]
    },
    "614": {
        "battle_type": 0,
        "enemies": [
            176,
            176,
            175
        ]
    },
    "616": {
        "battle_type": 0,
        "enemies": [
            175,
            175,
            174
        ]
    },
    "617": {
        "battle_type": 0,
        "enemies": [
            175,
            175,
            175
        ]
    },
    "632": {
        "battle_type": 0,
        "enemies": [
            186,
            186
        ]
    },
    "633": {
        "battle_type": 0,
        "enemies": [
            185
        ]
    },
    "634": {
        "battle_type": 0,
        "enemies": [
            186,
            186,
            189,
            189
        ]
    },
    "635": {
        "battle_type": 0,
        "enemies": [
            185,
            189,
            189
        ]
    },
    "636": {
        "battle_type": 0,
        "enemies": [
            191
        ]
    },
    "637": {
        "battle_type": 2,
        "enemies": [
            186,
            186
        ]
    },
    "638": {
        "battle_type": 2,
        "enemies": [
            186,
            189,
            189
        ]
    },
    "639": {
        "battle_type": 1,
        "enemies": [
            186,
            186
        ]
    },
    "640": {
        "battle_type": 0,
        "enemies": [
            192,
            192
        ]
    },
    "641": {
        "battle_type": 0,
        "enemies": [
            191
        ]
    },
    "642": {
        "battle_type": 0,
        "enemies": [
            192,
            192,
            192
        ]
    },
    "656": {
        "battle_type": 0,
        "enemies": [
            200,
            201,
            201,
            201
        ]
    },
    "657": {
        "battle_type": 0,
        "enemies": [
            201,
            201,
            201,
            201
        ]
    },
    "658": {
        "battle_type": 0,
        "enemies": [
            201,
            201,
            200,
            200,
            200
        ]
    },
    "659": {
        "battle_type": 0,
        "enemies": [
            203
        ]
    },
    "660": {
        "battle_type": 0,
        "enemies": [
            200,
            200,
            200
        ]
    },
    "661": {
        "battle_type": 0,
        "enemies": [
            198,
            200,
            200
        ]
    },
    "662": {
        "battle_type": 0,
        "enemies": [
            198,
            198,
        ]
    },
    "663": {
        "battle_type": 2,
        "enemies": [
            200,
            200,
            200
        ]
    },
    "664": {
        "battle_type": 0,
        "enemies": [
            202,
            202,
            202
        ]
    },
    "665": {
        "battle_type": 0,
        "enemies": [
            200,
            200,
            200,
            203
        ]
    },
    "666": {
        "battle_type": 0,
        "enemies": [
            200,
            200,
            200,
            200
        ]
    },
    "667": {
        "battle_type": 2,
        "enemies": [
            200,
            203,
            200
        ]
    },
    "668": {
        "battle_type": 0,
        "enemies": [
            204
        ]
    },
    "669": {
        "battle_type": 0,
        "enemies": [
            203,
            203
        ]
    },
    "672": {
        "battle_type": 0,
        "enemies": [
            206,
            206,
            206
        ]
    },
    "673": {
        "battle_type": 0,
        "enemies": [
            208,
            208
        ]
    },
    "674": {
        "battle_type": 0,
        "enemies": [
            206,
            206,
            208
        ]
    },
    "675": {
        "battle_type": 0,
        "enemies": [
            211,
            211
        ]
    },
    "676": {
        "battle_type": 0,
        "enemies": [
            208,
            208,
            208
        ]
    },
    "677": {
        "battle_type": 2,
        "enemies": [
            211,
            211
        ]
    },
    "680": {
        "battle_type": 0,
        "enemies": [
            207
        ]
    },
    "681": {
        "battle_type": 0,
        "enemies": [
            203,
            203,
            203
        ]
    },
    "682": {
        "battle_type": 0,
        "enemies": [
            211,
            211,
            211,
            211
        ]
    },
    "684": {
        "battle_type": 0,
        "enemies": [
            211,
            211,
            211
        ]
    },
    "685": {
        "battle_type": 0,
        "enemies": [
            205
        ]
    },
    "686": {
        "battle_type": 0,
        "enemies": [
            211,
            211
        ]
    },
    "687": {
        "battle_type": 0,
        "enemies": [
            210
        ]
    },
    "688": {
        "battle_type": 0,
        "enemies": [
            205,
            205
        ]
    },
    "689": {
        "battle_type": 2,
        "enemies": [
            211,
            211
        ]
    },
    "690": {
        "battle_type": 1,
        "enemies": [
            211,
            210,
            211
        ]
    },
    "691": {
        "battle_type": 2,
        "enemies": [
            211,
            211,
            211
        ]
    },
    "692": {
        "battle_type": 0,
        "enemies": [
            207,
            207
        ]
    },
    "693": {
        "battle_type": 0,
        "enemies": [
            211,
            211,
            211,
            211
        ]
    },
    "694": {
        "battle_type": 0,
        "enemies": [
            210,
            207
        ]
    },
    "695": {
        "battle_type": 0,
        "enemies": [
            210
        ]
    },
    "696": {
        "battle_type": 0,
        "enemies": [
            212
        ]
    },
    "697": {
        "battle_type": 0,
        "enemies": [
            212,
            212
        ]
    },
    "698": {
        "battle_type": 2,
        "enemies": [
            212
        ]
    },
    "700": {
        "battle_type": 0,
        "enemies": [
            218,
            218,
            218
        ]
    },
    "701": {
        "battle_type": 0,
        "enemies": [
            215
        ]
    },
    "702": {
        "battle_type": 0,
        "enemies": [
            220,
            220
        ]
    },
    "703": {
        "battle_type": 0,
        "enemies": [
            218,
            218,
            220
        ]
    },
    "704": {
        "battle_type": 2,
        "enemies": [
            218,
            218
        ]
    },
    "705": {
        "battle_type": 0,
        "enemies": [
            219
        ]
    },
    "706": {
        "battle_type": 0,
        "enemies": [
            218,
            220,
            218
        ]
    },
    "707": {
        "battle_type": 0,
        "enemies": [
            220,
            220,
            220,
            220
        ]
    },
    "708": {
        "battle_type": 0,
        "enemies": [
            221,
            221
        ]
    },
    "709": {
        "battle_type": 2,
        "enemies": [
            219
        ]
    },
    "711": {
        "battle_type": 0,
        "enemies": [
            221,
            221,
            221
        ]
    },
    "712": {
        "battle_type": 0,
        "enemies": [
            222,
            222
        ]
    },
    "713": {
        "battle_type": 0,
        "enemies": [
            222,
            218,
            218
        ]
    },
    "714": {
        "battle_type": 0,
        "enemies": [
            216
        ]
    },
    "715": {
        "battle_type": 2,
        "enemies": [
            222,
            222
        ]
    },
    "720": {
        "battle_type": 0,
        "enemies": [
            224
        ]
    },
    "721": {
        "battle_type": 0,
        "enemies": [
            223
        ]
    },
    "722": {
        "battle_type": 0,
        "enemies": [
            224,
            224
        ]
    },
    "724": {
        "battle_type": 0,
        "enemies": [
            225,
            225,
            225
        ]
    },
    "725": {
        "battle_type": 0,
        "enemies": [
            227,
            227
        ]
    },
    "726": {
        "battle_type": 0,
        "enemies": [
            226
        ]
    },
    "727": {
        "battle_type": 0,
        "enemies": [
            225,
            225,
            227
        ]
    },
    "728": {
        "battle_type": 2,
        "enemies": [
            225,
            225
        ]
    },
    "730": {
        "battle_type": 0,
        "enemies": [
            230,
            230
        ]
    },
    "731": {
        "battle_type": 0,
        "enemies": [
            231
        ]
    },
    "732": {
        "battle_type": 0,
        "enemies": [
            226,
            230,
            230
        ]
    },
    "733": {
        "battle_type": 0,
        "enemies": [
            226,
            226
        ]
    },
    "734": {
        "battle_type": 2,
        "enemies": [
            230,
            230
        ]
    },
    "736": {
        "battle_type": 0,
        "enemies": [
            232,
            232
        ]
    },
    "737": {
        "battle_type": 0,
        "enemies": [
            225,
            225,
            232
        ]
    },
    "738": {
        "battle_type": 0,
        "enemies": [
            233
        ]
    },
    "739": {
        "battle_type": 0,
        "enemies": [
            233
        ]
    },
    "744": {
        "battle_type": 0,
        "enemies": [
            235
        ]
    },
    "745": {
        "battle_type": 0,
        "enemies": [
            237,
            237
        ]
    },
    "746": {
        "battle_type": 0,
        "enemies": [
            237,
            235,
            237
        ]
    },
    "748": {
        "battle_type": 0,
        "enemies": [
            239,
            239
        ]
    },
    "749": {
        "battle_type": 0,
        "enemies": [
            239,
            239,
            239
        ]
    },
    "750": {
        "battle_type": 0,
        "enemies": [
            238
        ]
    },
    "751": {
        "battle_type": 2,
        "enemies": [
            239,
            239
        ]
    },
    "752": {
        "battle_type": 1,
        "enemies": [
            238
        ]
    },
    "753": {
        "battle_type": 0,
        "enemies": [
            238,
            238
        ]
    },
    "754": {
        "battle_type": 0,
        "enemies": [
            239,
            239,
            237
        ]
    },
    "755": {
        "battle_type": 2,
        "enemies": [
            237,
            237
        ]
    },
    "756": {
        "battle_type": 0,
        "enemies": [
            243
        ]
    },
    "757": {
        "battle_type": 0,
        "enemies": [
            243,
            243
        ]
    },
    "761": {
        "battle_type": 0,
        "enemies": [
            237,
            237,
            237
        ]
    },
    "762": {
        "battle_type": 0,
        "enemies": [
            237,
            237
        ]
    },
    "764": {
        "battle_type": 0,
        "enemies": [
            248
        ]
    },
    "765": {
        "battle_type": 0,
        "enemies": [
            246
        ]
    },
    "766": {
        "battle_type": 0,
        "enemies": [
            247,
            247
        ]
    },
    "772": {
        "battle_type": 0,
        "enemies": [
            252,
            257
        ]
    },
    "773": {
        "battle_type": 0,
        "enemies": [
            253,
            253
        ]
    },
    "774": {
        "battle_type": 0,
        "enemies": [
            253,
            252,
            252
        ]
    },
    "775": {
        "battle_type": 2,
        "enemies": [
            257,
            252
        ]
    },
    "776": {
        "battle_type": 0,
        "enemies": [
            254
        ]
    },
    "777": {
        "battle_type": 0,
        "enemies": [
            254,
            254
        ]
    },
    "778": {
        "battle_type": 2,
        "enemies": [
            254
        ]
    },
    "788": {
        "battle_type": 0,
        "enemies": [
            261,
            261,
            261
        ]
    },
    "789": {
        "battle_type": 0,
        "enemies": [
            263,
            263
        ]
    },
    "790": {
        "battle_type": 0,
        "enemies": [
            262
        ]
    },
    "791": {
        "battle_type": 0,
        "enemies": [
            262,
            261,
            261
        ]
    },
    "792": {
        "battle_type": 2,
        "enemies": [
            261,
            261
        ]
    },
    "793": {
        "battle_type": 1,
        "enemies": [
            261,
            261,
            261
        ]
    },
    "794": {
        "battle_type": 2,
        "enemies": [
            261,
            261,
            261
        ]
    },
    "796": {
        "battle_type": 0,
        "enemies": [
            269,
            269
        ]
    },
    "797": {
        "battle_type": 0,
        "enemies": [
            269,
            270,
            270
        ]
    },
    "798": {
        "battle_type": 0,
        "enemies": [
            270,
            270,
            270,
            270
        ]
    },
    "800": {
        "battle_type": 0,
        "enemies": [
            271
        ]
    },
    "801": {
        "battle_type": 0,
        "enemies": [
            272
        ]
    },
    "802": {
        "battle_type": 0,
        "enemies": [
            273
        ]
    },
    "803": {
        "battle_type": 2,
        "enemies": [
            271
        ]
    },
    "804": {
        "battle_type": 0,
        "enemies": [
            268
        ]
    },
    "820": {
        "battle_type": 0,
        "enemies": [
            286,
            286
        ]
    },
    "821": {
        "battle_type": 0,
        "enemies": [
            286,
            286,
            286
        ]
    },
    "822": {
        "battle_type": 0,
        "enemies": [
            287,
            287,
            287
        ]
    },
    "823": {
        "battle_type": 0,
        "enemies": [
            287,
            287,
            287
        ]
    },
    "824": {
        "battle_type": 0,
        "enemies": [
            285
        ]
    },
    "825": {
        "battle_type": 0,
        "enemies": [
            289,
            289
        ]
    },
    "826": {
        "battle_type": 0,
        "enemies": [
            289,
            286
        ]
    },
    "827": {
        "battle_type": 2,
        "enemies": [
            286
        ]
    },
    "828": {
        "battle_type": 2,
        "enemies": [
            286,
            286
        ]
    },
    "830": {
        "battle_type": 0,
        "enemies": [
            289
        ]
    },
    "831": {
        "battle_type": 0,
        "enemies": [
            290,
            290
        ]
    },
    "832": {
        "battle_type": 0,
        "enemies": [
            290,
            290,
            290
        ]
    },
    "833": {
        "battle_type": 0,
        "enemies": [
            290,
            290,
            289
        ]
    },
    "834": {
        "battle_type": 2,
        "enemies": [
            290,
            290
        ]
    },
    "835": {
        "battle_type": 2,
        "enemies": [
            289
        ]
    },
    "836": {
        "battle_type": 0,
        "enemies": [
            293
        ]
    },
    "837": {
        "battle_type": 0,
        "enemies": [
            293
        ]
    },
    "838": {
        "battle_type": 0,
        "enemies": [
            293
        ]
    },
    "839": {
        "battle_type": 0,
        "enemies": [
            293
        ]
    },
    "848": {
        "battle_type": 0,
        "enemies": [
            301,
            301
        ]
    },
    "849": {
        "battle_type": 0,
        "enemies": [
            302
        ]
    },
    "850": {
        "battle_type": 0,
        "enemies": [
            301,
            301,
            301
        ]
    },
    "851": {
        "battle_type": 2,
        "enemies": [
            301,
            301
        ]
    },
    "852": {
        "battle_type": 0,
        "enemies": [
            304
        ]
    },
    "853": {
        "battle_type": 0,
        "enemies": [
            301
        ]
    },
    "868": {
        "battle_type": 0,
        "enemies": [
            294,
            295
        ]
    },
    "869": {
        "battle_type": 0,
        "enemies": [
            294,
            295,
            294,
            295
        ]
    },
    "870": {
        "battle_type": 0,
        "enemies": [
            322
        ]
    },
    "872": {
        "battle_type": 0,
        "enemies": [
            317
        ]
    },
    "873": {
        "battle_type": 0,
        "enemies": [
            321,
            321
        ]
    },
    "874": {
        "battle_type": 0,
        "enemies": [
            321,
            321,
            321
        ]
    },
    "875": {
        "battle_type": 2,
        "enemies": [
            321,
            321
        ]
    },
    "876": {
        "battle_type": 0,
        "enemies": [
            318
        ]
    },
    "877": {
        "battle_type": 0,
        "enemies": [
            323,
            323
        ]
    },
    "878": {
        "battle_type": 0,
        "enemies": [
            318,
            321,
            321
        ]
    },
    "879": {
        "battle_type": 0,
        "enemies": [
            321,
            321,
            321
        ]
    },
    "880": {
        "battle_type": 0,
        "enemies": [
            215
        ]
    },
    "881": {
        "battle_type": 0,
        "enemies": [
            315
        ]
    },
    "882": {
        "battle_type": 2,
        "enemies": [
            323
        ]
    },
    "884": {
        "battle_type": 0,
        "enemies": [
            311,
            312
        ]
    },
    "885": {
        "battle_type": 0,
        "enemies": [
            310
        ]
    },
    "886": {
        "battle_type": 0,
        "enemies": [
            310,
            310
        ]
    },
    "889": {
        "battle_type": 0,
        "enemies": [
            314
        ]
    },
    "890": {
        "battle_type": 0,
        "enemies": [
            319,
            319,
            319
        ]
    },
    "891": {
        "battle_type": 0,
        "enemies": [
            317
        ]
    },
    "892": {
        "battle_type": 0,
        "enemies": [
            313
        ]
    },
    "893": {
        "battle_type": 0,
        "enemies": [
            314
        ]
    },
    "894": {
        "battle_type": 0,
        "enemies": [
            316
        ]
    },
    "895": {
        "battle_type": 2,
        "enemies": [
            314
        ]
    },
    "896": {
        "battle_type": 0,
        "enemies": [
            317
        ]
    },
    "940": {
        "battle_type": 0,
        "enemies": [
            237
        ]
    },
    "941": {
        "battle_type": 0,
        "enemies": [
            235
        ]
    },
    "942": {
        "battle_type": 0,
        "enemies": [
            237,
            237
        ]
    },
    "944": {
        "battle_type": 0,
        "enemies": [
            237
        ]
    },
    "945": {
        "battle_type": 0,
        "enemies": [
            237,
            237
        ]
    },
    "948": {
        "battle_type": 0,
        "enemies": [
            240
        ]
    },
    "949": {
        "battle_type": 0,
        "enemies": [
            240,
            240
        ]
    },
    "950": {
        "battle_type": 2,
        "enemies": [
            240
        ]
    },
    "976": {
        "battle_type": 0,
        "enemies": [
            262,
            262
        ]
    },
    "977": {
        "battle_type": 0,
        "enemies": [
            261,
            261,
            263
        ]
    },
    "978": {
        "battle_type": 0,
        "enemies": [
            262
        ]
    },
    "979": {
        "battle_type": 2,
        "enemies": [
            262,
            262
        ]
    }
}
