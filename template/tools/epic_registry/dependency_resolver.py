"""
Dependency resolution and graph analysis.
"""

from typing import Dict, List, Optional, Set
from .models import Epic, EpicRegistryData


def get_dependency_graph(registry_data: EpicRegistryData) -> Dict[str, List[str]]:
    """
    Build dependency graph (adjacency list).

    Returns:
        Dict mapping epic_id to list of epic_ids it depends on (blocked_by)
    """
    graph = {}

    for epic in registry_data.epics:
        graph[epic.epic_id] = epic.dependencies.blocked_by.copy()

    return graph


def find_dependency_cycle(registry_data: EpicRegistryData) -> Optional[List[str]]:
    """
    Detect circular dependencies.

    Returns:
        List of epic IDs forming a cycle, or None if no cycle
    """
    graph = get_dependency_graph(registry_data)
    visited = set()
    rec_stack = set()

    def dfs(node: str, path: List[str]) -> Optional[List[str]]:
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                cycle = dfs(neighbor, path.copy())
                if cycle:
                    return cycle
            elif neighbor in rec_stack:
                # Found cycle
                cycle_start = path.index(neighbor)
                return path[cycle_start:] + [neighbor]

        rec_stack.remove(node)
        return None

    for epic_id in graph:
        if epic_id not in visited:
            cycle = dfs(epic_id, [])
            if cycle:
                return cycle

    return None


def topological_sort(registry_data: EpicRegistryData) -> List[str]:
    """
    Topological sort of epics (dependency-respecting order).

    Returns:
        List of epic IDs in execution order

    Raises:
        ValueError if cycle detected
    """
    graph = get_dependency_graph(registry_data)
    in_degree = {epic.epic_id: 0 for epic in registry_data.epics}

    # Calculate in-degrees
    for epic_id, deps in graph.items():
        for dep in deps:
            if dep in in_degree:
                in_degree[dep] += 1

    # Find all nodes with in-degree 0
    queue = [epic_id for epic_id, degree in in_degree.items() if degree == 0]
    result = []

    while queue:
        node = queue.pop(0)
        result.append(node)

        # Reduce in-degree for neighbors
        for epic_id, deps in graph.items():
            if node in deps:
                in_degree[epic_id] -= 1
                if in_degree[epic_id] == 0:
                    queue.append(epic_id)

    if len(result) != len(registry_data.epics):
        raise ValueError("Circular dependency detected")

    return result
