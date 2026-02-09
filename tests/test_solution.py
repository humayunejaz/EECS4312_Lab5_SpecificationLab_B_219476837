from src.solution import is_allocation_feasible


def test_simple_feasible():
    requests = [{"A": 1}]
    available = {"A": 2}
    assert is_allocation_feasible(requests, available) is True


def test_simple_infeasible_capacity():
    requests = [{"A": 3}]
    available = {"A": 2}
    assert is_allocation_feasible(requests, available) is False


def test_multiple_requests_with_options():
    requests = [
        [{"A": 1}, {"B": 1}],
        [{"A": 1}],
    ]
    available = {"A": 2, "B": 1}
    assert is_allocation_feasible(requests, available) is True


# 🔴 NEW REQUIREMENT TEST — should now FAIL
def test_all_resources_consumed_is_invalid():
    requests = [{"A": 1}, {"B": 1}]
    available = {"A": 1, "B": 1}
    assert is_allocation_feasible(requests, available) is False


# 🟢 NEW REQUIREMENT TEST — leftover exists
def test_leftover_resource_valid():
    requests = [{"A": 1}]
    available = {"A": 1, "B": 1}
    assert is_allocation_feasible(requests, available) is True

