from typing import Dict, List


def is_allocation_feasible(requests, available_resources) -> bool:
    """
    Returns True iff all requests can be satisfied within available_resources
    AND at least one resource unit remains unallocated.
    """

    # Defensive copies
    capacities: Dict[str, int] = dict(available_resources)

    # No requests: valid only if at least one resource unit exists
    if not requests:
        return any(v > 0 for v in capacities.values())

    # Normalize requests:
    # Each request becomes a list of allocation options (dicts)
    normalized = []
    for r in requests:
        if isinstance(r, list):
            # multiple options
            normalized.append(r)
        else:
            # single option
            normalized.append([r])

    def backtrack(i: int, remaining: Dict[str, int]) -> bool:
        # All requests assigned → check leftover condition
        if i == len(normalized):
            return any(v > 0 for v in remaining.values())

        for option in normalized[i]:
            # Check if option fits
            fits = True
            for res, amt in option.items():
                if remaining.get(res, 0) < amt:
                    fits = False
                    break

            if not fits:
                continue

            # Apply allocation
            for res, amt in option.items():
                remaining[res] -= amt

            if backtrack(i + 1, remaining):
                return True

            # Undo allocation
            for res, amt in option.items():
                remaining[res] += amt

        return False

    return backtrack(0, capacities)
