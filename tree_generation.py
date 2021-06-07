#!/usr/bin/env python

"""Implementation of the Wright, Richmond, Odlyzko and McKay (WROM)
algorithm for the enumeration of all non-isomorphic free trees of a
given order.  Rooted trees are represented by level sequences, i.e.,
lists in which the i-th element specifies the distance of vertex i to
the root."""

import sys

def trees(order):
	"""Generate all the non-isomorphic free trees of the given
	order.
    layout encodes a representation of a graph.
    """

	# We initialize the algorithm with the path graph rooted at its center
	layout = list(range(int(order / 2) + 1)) + list(range(1, int((order + 1) / 2)))

	while layout is not None:
		layout = next_tree(layout)
		if layout != None:
			yield layout_to_matrix(layout)
			layout = next_rooted_tree(layout)

def next_rooted_tree(predecessor, p=None):
	"""One iteration of the Beyer-Hedetniemi algorithm."""

	if p is None:
		p = len(predecessor) - 1
		while predecessor[p] == 1:
			p -= 1
	if p == 0:
		return None

	q = p - 1
	while predecessor[q] != predecessor[p] - 1:
		q -= 1
	result = list(predecessor)
	for i in range(p, len(result)):
		result[i] = result[i - p + q]
	return result

def next_tree(candidate):
	"""One iteration of the Wright, Richmond, Odlyzko and McKay
	algorithm."""

	# valid representation of a free tree if:
	# there are at least two vertices at layer 1
	# (this is always the case because we start at the path graph)
	left, rest = split_tree(candidate)

	# and the left subtree of the root
	# is less high than the tree with the left subtree removed
	left_height = max(left)
	rest_height = max(rest)
	valid = rest_height >= left_height

	if valid and rest_height == left_height:
		# and, if left and rest are of the same height,
		# if left does not encompass more vertices
		if len(left) > len(rest):
			valid = False
		# and, if they have the same number or vertices,
		# if left does not come after rest lexicographically
		elif len(left) == len(rest) and left > rest:
			valid = False

	if valid:
		return candidate
	else:
		# jump to the next valid free tree
		p = len(left)
		new_candidate = next_rooted_tree(candidate, p)
		if candidate[p] > 2:
			new_left, new_rest = split_tree(new_candidate)
			new_left_height = max(new_left)
			suffix = range(1, new_left_height + 2)
			new_candidate[-len(suffix):] = suffix
		return new_candidate

def split_tree(layout):
	"""Return a tuple of two layouts, one containing the left
	subtree of the root vertex, and one containing the original tree
	with the left subtree removed."""

	one_found = False
	m = None
	for i in range(len(layout)):
		if layout[i] == 1:
			if one_found:
				m = i
				break
			else:
				one_found = True

	if m is None:
		m = len(layout)

	left = [layout[i] - 1 for i in range(1, m)]
	rest = [0] + [layout[i] for i in range(m, len(layout))]
	return (left, rest)

def layout_to_matrix(layout):
	"""Create the adjacency matrix for the tree specified by the
	given layout (level sequence)."""

	result = [[0] * len(layout) for i in range(len(layout))]

	stack = []
	for i in range(len(layout)):
		i_level = layout[i]
		if stack:
			j = stack[-1]
			j_level = layout[j]
			while j_level >= i_level:
				stack.pop()
				j = stack[-1]
				j_level = layout[j]
			result[i][j] = result[j][i] = 1
		stack.append(i)

	return result


order = 4

generator = trees(5)
for t in generator:
    print(t)

#import functools
#print(functools.reduce(lambda accum, tree: accum + 1, generator, 0)


