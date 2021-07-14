def get_preempt_rate(preempt_equipped: int, preempt_stars: int):
    return max(16, min(128, 16 + (32 * preempt_stars) - (16 * preempt_equipped)))
