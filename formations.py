from constants import *


def encounter_on_formation(field: Field, formation: int, preempt_rate: int = 16,
                           table: int = 1):
    tbl = field.table1 if table == 1 or field.table2 is None else field.table2

    comparison_value = 0

    formation = (formation + 1) % 256
    fm_rng = RNG[formation] // 4
    # back attack 1
    if preempt_rate < 128:
        comparison_value += tbl.special[0].rate
    else:
        comparison_value += tbl.special[0].rate // 2
    if fm_rng < comparison_value:
        return tbl.special[0].formation, None, "Back Attack"
    # back attack 2
    if preempt_rate < 128:
        comparison_value += tbl.special[1].rate
    else:
        comparison_value += tbl.special[1].rate // 2
    if fm_rng < comparison_value:
        return tbl.special[1].formation, None, "Back Attack"
    # side attack
    comparison_value += tbl.special[2].rate
    if fm_rng < comparison_value:
        return tbl.special[2].formation, None, "Side Attack"
    # pincer
    if preempt_rate < 128:
        comparison_value += tbl.special[3].rate
    else:
        comparison_value += tbl.special[3].rate // 2
    if fm_rng < comparison_value:
        return tbl.special[3].formation, None, "Pincer Attack"

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

    # hardcoded exception because of a glitch in FF7
    if tbl.standard[0].rate > 32:
        return tbl.standard[0].formation, tbl.standard[0].formation, "Normal"

    for i in range(5):
        comparison_value += tbl.standard[i].rate
        if fm_rng < comparison_value:
            return encounter, tbl.standard[i].formation, "Normal"

    return encounter, tbl.standard[5].formation, "Normal"
