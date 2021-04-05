from constants import *
import copy


def get_preempt_rate(preempt_equipped: int, preempt_stars: int):
    return max(16, min(128, 16 + (32 * preempt_stars) - (16 * preempt_equipped)))


def encounter_at_step(step: Step, preempt_rate: int = 16):
    step = copy.copy(step)
    danger_threshold = (((RNG[step.stepid] - step.offset) % 256) + 1) * 256
    # step.advance_steps(-1)
    # if step.stepid == 2:
    #     breakpoint()
    preempt_threhsold = ((RNG[step.stepid - 1] - step.offset) % 256)
    preempt = preempt_threhsold < max(16, min(128, preempt_rate))
    return danger_threshold, preempt, preempt_threhsold


def encounter_on_formation(field: Field, formation: int, last_encounter: int = None, preempt_rate: int = 16,
                           table: int = 0):
    tbl = field.table1 if table == 0 or field.table2 is None else field.table2

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

    # if last_encounter is None or last_encounter != encounter:
    #     return encounter, formation, "Normal"

    formation2 = (formation + 1) % 256
    fm_rng = RNG[formation2] // 4
    comparison_value = 0

    for i in range(5):
        comparison_value += tbl.standard[i].rate
        if fm_rng < comparison_value:
            return encounter, tbl.standard[i].formation, "Normal"
    return encounter, tbl.standard[5].formation, "Normal"
