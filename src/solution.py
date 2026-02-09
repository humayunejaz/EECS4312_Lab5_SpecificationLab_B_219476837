## Student Name: Humayun Ejaz
## Student ID: 219476837

from collections import Counter
from typing import Any, Dict, List, Tuple

def is_allocation_feasible(requests, available_resources) -> bool:
    """
    Robust feasibility checker for resource allocation problems.

    Supports common input styles:
    - available_resources as dict: {"CPU": 4, "RAM": 16}
    - requests as:
        A) dict totals: {"CPU": 2, "RAM": 8}
        B) list of dicts (each request is a bundle): [{"CPU": 1}, {"CPU": 1, "RAM": 4}]
        C) list of (resource, amount): [("CPU", 1), ("RAM", 4)]
        D) list of options per request:
             [
               [{"CPU": 1}, {"GPU": 1}],   # request 1 can be satisfied by either option
               [{"RAM": 4}]                # request 2
             ]
        E) list of acceptable resources (unit demand):
             [ {"CPU","GPU"}, {"CPU"} ]  or  [ ["CPU","GPU"], ["CPU"] ]
    Returns True if there exists an allocation that satisfies all requests within capacities.
    """

    # ---------- helpers: normalize capacities ----------
    def normalize_capacities(av: Any) -> Dict[str, int]:
        if av is None:
            return {}
        if isinstance(av, dict):
            caps = {}
            for k, v in av.items():
                if v is None:
                    return {}
                caps[str(k)] = int(v)
            return caps
        # if it's a list/tuple of (name, cap)
        if isinstance(av, (list, tuple)):
            caps = {}
            for item in av:
                if isinstance(item, (list, tuple)) and len(item) == 2:
                    caps[str(item[0])] = int(item[1])
                else:
                    # unknown format
                    return {}
            return caps
        return {}

    # ---------- helpers: normalize requests into "options" ----------
    # We convert every request into a list of "choices"; each choice is a dict resource->amount.
    def normalize_requests(reqs: Any) -> List[List[Dict[str, int]]]:
        if reqs is None:
            return []

        # Case A: dict totals (single "bundle request")
        if isinstance(reqs, dict):
            bundle = {str(k): int(v) for k, v in reqs.items()}
            return [[bundle]]

        # Case B/C/D/E: list-like
        if not isinstance(reqs, (list, tuple)):
            return []

        out: List[List[Dict[str, int]]] = []

        for r in reqs:
            # D) already a list of options: e.g. [ {"CPU":1}, {"GPU":1} ]
            if isinstance(r, (list, tuple)) and len(r) > 0 and all(isinstance(x, dict) for x in r):
                opts = []
                for opt in r:
                    opts.append({str(k): int(v) for k, v in opt.items()})
                out.append(opts)
                continue

            # E) a set/list of acceptable resources for unit demand
            if isinstance(r, (set, list, tuple)) and (len(r) == 0 or all(not isinstance(x, dict) for x in r)):
                # interpret as "choose ONE resource name, amount 1"
                opts = [{str(name): 1} for name in r]
                out.append(opts)
                continue

            # B) a dict bundle per request
            if isinstance(r, dict):
                out.append([{str(k): int(v) for k, v in r.items()}])
                continue

            # C) a (resource, amount) tuple
            if isinstance(r, (list, tuple)) and len(r) == 2 and not isinstance(r[0], (list, tuple, dict, set)):
                out.append([{str(r[0]): int(r[1])}])
                continue

            # C-alt) a single resource name means unit demand
            if isinstance(r, str):
                out.append([{r: 1}])
                continue

            # Unknown request format
            return []

        return out

    caps = normalize_capacities(available_resources)
    req_options = normalize_requests(requests)

    # If parsing failed badly, be conservative
    if available_resources is None or caps == {} and available_resources not in ({}, []):
        # If they passed something non-empty but we couldn't parse, fail
        # (If spec expects exceptions instead, adjust here)
        return False

    # No requests => feasible
    if len(req_options) == 0:
        return True

    # Quick infeasibility check: any option requires a resource not in caps or negative amounts
    for opts in req_options:
        if len(opts) == 0:
            return False
        for opt in opts:
            for k, v in opt.items():
                if v < 0:
                    return False
                if k not in caps:
                    # If resource missing, that option is invalid; don't kill whole request yet
                    pass

    # Remove invalid options that reference unknown resources or exceed caps individually
    cleaned: List[List[Dict[str, int]]] = []
    for opts in req_options:
        valid = []
        for opt in opts:
            ok = True
            for k, v in opt.items():
                if k not in caps:
                    ok = False
                    break
                if v > caps[k]:
                    ok = False
                    break
            if ok:
                valid.append(opt)
        if not valid:
            return False
        cleaned.append(valid)

    req_options = cleaned

    # Sort requests hardest-first to prune faster (fewest options, biggest demand)
    def demand_size(opt: Dict[str, int]) -> int:
        return sum(opt.values())

    req_options.sort(key=lambda opts: (len(opts), -max(demand_size(o) for o in opts)))

    # Backtracking with memoization on remaining capacities
    cap_keys = tuple(sorted(caps.keys()))

    def caps_to_state(c: Dict[str, int]) -> Tuple[int, ...]:
        return tuple(c[k] for k in cap_keys)

    memo = set()

    def can_fit(opt: Dict[str, int], c: Dict[str, int]) -> bool:
        for k, v in opt.items():
            if c[k] < v:
                return False
        return True

    def apply(opt: Dict[str, int], c: Dict[str, int], sign: int) -> None:
        for k, v in opt.items():
            c[k] += sign * (-v)  # sign=+1 => subtract v, sign=-1 => add back v

    def dfs(i: int, c: Dict[str, int]) -> bool:
        state = (i, caps_to_state(c))
        if state in memo:
            return False
        if i == len(req_options):
            return True

        opts = req_options[i]
        # Try each option
        for opt in opts:
            if can_fit(opt, c):
                apply(opt, c, +1)
                if dfs(i + 1, c):
                    return True
                apply(opt, c, -1)

        memo.add(state)
        return False

    return dfs(0, dict(caps))
