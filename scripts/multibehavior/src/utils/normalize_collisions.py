import numpy as np

def normalize_collision_positions(collision_pos):
    """
    Takes a single collision_pos entry and returns
    a list of (x, y) tuples.
    """
    if collision_pos is None:
        return []

    arr = np.array(collision_pos, dtype=float)

    # Case: single point like (2,) → reshape
    if arr.ndim == 1 and arr.size == 2:
        return [tuple(arr)]

    # Case: multiple points → reshape safely
    if arr.ndim == 2 and arr.shape[1] == 2:
        return [tuple(p) for p in arr]

    raise ValueError(f"Unexpected collision_pos shape: {arr.shape}")
