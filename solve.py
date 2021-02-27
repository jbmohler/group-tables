#!/usr/bin/python
import sys
import copy
import random
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

alphabet = args.alphabet
if not alphabet:
    alphabet = list(range(order))

identity = args.identity
if not identity:
    identity = alphabet[0]
if identity not in alphabet:
    args.print_help()
    sys.exit(1)

# stub out the grid matching the identity axiom
s2 = sudoku2.group_identity(order, alphabet, identity)
for _ in range(2):
    s2.shuffle()

    inv = copy.deepcopy(s2)

    eligible = lambda cell: isinstance(cell, list) and identity in cell
    # set the identities symmetrically accross the diagonal to satisfy
    # the inverse axiom
    for index, elt in enumerate(alphabet):
        if index == 0:
            continue

        possibilities = [
            ii for ii, _ in enumerate(alphabet) if eligible(inv[(index, ii)])
        ]

        if not possibilities:
            continue

        inv_index = random.choice(possibilities)
        inv.fix_point((index, inv_index), identity)
        inv.fix_point((inv_index, index), identity)

    # complete matching the closure axiom
    try:
        grp = inv.solve()
    except sudoku2.Impossible:
        print("failed on impossible inverse choices")
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
