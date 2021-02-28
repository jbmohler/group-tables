#!/usr/bin/python
import sys
import copy
import random
import itertools
import string
import argparse
import sudoku2

parser = argparse.ArgumentParser()
parser.add_argument("--order", default=4, help="the order of the group to generate")
parser.add_argument(
    "--alphabet", help="symbols for group members -- (0-order) if not given"
)
parser.add_argument("--identity", help="identity element from alphabet")
args = parser.parse_args()

# s2 = sudoku2.Sudoku_FromFile( args.puzzle_file )

order = int(args.order)
if order <= 0:
    print("the group order must be greater than 0")
    args.print_help()
    sys.exit(1)

alphabet = args.alphabet

if alphabet == "star-alpha":
    alphabet = ("*" + string.ascii_lowercase)[:order]

if not alphabet:
    alphabet = list(range(order))

identity = args.identity
if not identity:
    identity = alphabet[0]
if identity not in alphabet:
    args.print_help()
    sys.exit(1)


def my_complete(_board):
    grp = sudoku2.GroupBoard(size=order, alphabet=alphabet)
    grp.board = _board

    # monte carlo checks of the associative axiom
    # (no real analysis has been made about how many checks are required)
    for _ in range(order):
        a, b, c = random.choices(alphabet, k=3)

        op = grp.group_op

        r1 = op(a, op(b, c))
        r2 = op(op(a, b), c)

        if r1 != r2:
            fails = True
            break
    else:
        fails = False

    if fails:
        print("solution failed associative axiom")
        return

    print(grp)

    # for e in alphabet:
    #    print(grp.left_order(e), grp.right_order(e))

    print("-" * 40)


def symmetric_permutations(elts):
    prior = set()
    indexes = {e: index for index, e in enumerate(elts)}
    for perm in itertools.permutations(elts):
        perm_prune = tuple([p if indexes[p] >= i else None for i, p in enumerate(perm)])
        if perm_prune in prior:
            continue
        else:
            prior.add(perm_prune)
            yield perm_prune


# stub out the grid matching the identity axiom
s2 = sudoku2.group_identity(order, alphabet, identity)

s2.config.completed = my_complete

# for inverses in symmetric_permutations(alphabet[1:]):

parity = (order - 1) % 2

for c2_idx in range((order - 1) // 2 + 1):
    s2.shuffle()

    inv = copy.deepcopy(s2)

    eligible = lambda cell: isinstance(cell, list) and identity in cell

    # By the inverse axiom inverse elements come in either mutually inverse
    # pairs unless the element is its own inverse.  For visual effect, we group
    # an even number of order 2 elements towards the origin and the rest of the
    # elements in order so that the identities in group operation table form a
    # diagonal line perpendicular to the main diagonal.

    # Note that the identities symmetrically accross the diagonal to satisfy
    # the inverse axiom

    count2 = 2 * c2_idx

    try:
        # for _index, elt in enumerate(inverses):
        #    if elt != None:
        #        index = _index + 1
        #        inv_index = alphabet.index(elt)
        #        inv.fix_point((index, inv_index), identity)
        #        inv.fix_point((inv_index, index), identity)

        for index in range(1, 2 * c2_idx + 1):
            inv.fix_point((index, index), identity)
        for index in range(1 + 2 * c2_idx, order):
            inv.fix_point((index, order - index), identity)
    except sudoku2.Impossible:
        print("failed on impossible inverse choices")
        continue


    # complete matching the closure axiom
    try:
        grp = inv.solve()
    except sudoku2.Impossible:
        print("failed on impossible inverse choices")
        continue

    continue

    # monte carlo checks of the associative axiom
    # (no real analysis has been made about how many checks are required)
    for _ in range(order):
        a, b, c = random.choices(alphabet, k=3)

        op = grp.group_op

        r1 = op(a, op(b, c))
        r2 = op(op(a, b), c)

        if r1 != r2:
            fails = True
            break
    else:
        fails = False

    if fails:
        print("solution failed associative axiom")
        continue

    print(grp)

    for e in alphabet:
        print(grp.left_order(e), grp.right_order(e))

    print("-" * 40)

    # print("Original:")
    # print(s2)
