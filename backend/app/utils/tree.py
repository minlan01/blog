"""Recursive tree utilities for collecting descendant IDs.

Used by comments, messages, and admin endpoints to handle
self-referential parent-child relationships.
"""
from typing import Callable, TypeVar

T = TypeVar("T")


def collect_descendant_ids(
    root_id: int,
    get_children: Callable[[int], list[tuple[int, ...]]],
) -> list[int]:
    """Recursively collect all descendant IDs of a given root.

    Args:
        root_id: The ID of the root node to start from.
        get_children: A function that takes a parent ID and returns
                      a list of tuples where the first element is the child ID.

    Returns:
        A flat list of all descendant IDs (not including root_id).
    """
    result: list[int] = []
    children = get_children(root_id)
    for child in children:
        child_id = child[0]
        result.append(child_id)
        result.extend(collect_descendant_ids(child_id, get_children))
    return result
