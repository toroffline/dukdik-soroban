import random

def generate_valid_sequence(mode=1, length=5):
    """Generates valid steps based on active difficulty mode."""
    sequence = []
    current_val = 0
    
    if mode == 1:
        possible_deltas = [1, 2, 3, 4, 5, 6, 7, 8, 9, -1, -2, -3, -4, -5, -6, -7, -8, -9]
    elif mode == 2:
        possible_deltas = [
            1, 2, 3, 4, 5, -1, -2, -3, -4, -5,
            10, 12, 15, 20, 25, 50, -10, -12, -15, -20, -25, -50
        ]
    else:
        possible_deltas = [
            1, 2, 3, 4, 5, -1, -2, -3, -4, -5,
            10, 20, 50, -10, -20, -50,
            100, 250, 500, -100, -250, -500
        ]
    
    for _ in range(length):
        valid_step_found = False
        attempts = 0
        while not valid_step_found and attempts < 100:
            attempts += 1
            step = random.choice(possible_deltas)
            new_total = current_val + step
            
            if 0 <= new_total <= 99999 and step != 0:
                if current_val == 0 and step < 0:
                    continue
                sequence.append(step)
                current_val = new_total
                valid_step_found = True

    return sequence, current_val


class SorobanEngine:
    def __init__(self):
        self.beads = [0, 0, 0, 0, 0]  # [10000s, 1000s, 100s, 10s, 1s]
        self.active_col = 4           # Default to 1s column
        self.prefix = 1

    def get_current_value(self):
        multipliers = [10000, 1000, 100, 10, 1]
        return sum(self.beads[i] * multipliers[i] for i in range(5))

    def apply_smart_delta(self, delta):
        target_val = self.beads[self.active_col] + delta
        if 0 <= target_val <= 9:
            self.beads[self.active_col] = target_val

    def reset_beads(self):
        self.beads = [0, 0, 0, 0, 0]
        self.prefix = 1
        self.active_col = 4

