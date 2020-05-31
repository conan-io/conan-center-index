#!/usr/bin/env python

# Running autoreconf on a modified configure.ac script, will result in a huge diff because of all the line number differences
# This script attempts to reduce the delta by removing the hunks where only line numbers are modified
# This script is very crude in that it only checks whether a number is changed.

import argparse
import patch_ng
import string


def hunk_contains_only_line_diff(hunk: patch_ng.Hunk):
    adds = []
    subs = []
    digits_remove = bytes.maketrans(string.digits.encode(), ("X" * len(string.digits)).encode())
    for line in hunk.text:
        if line[0] == ord("+"):
            adds.append(line[1:].translate(digits_remove))
        elif line[0] == ord("-"):
            subs.append(line[1:].translate(digits_remove))
    return adds == subs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input file")
    parser.add_argument("-o", dest="output", help="output file")
    ns = parser.parse_args()
    patchset: patch_ng.PatchSet = patch_ng.fromfile(ns.input)
    if not patchset:
        return 1

    for item in patchset.items:
        if item.source != "configure":
            pass
        item.hunks = [hunk for hunk in item.hunks if not hunk_contains_only_line_diff(hunk)]

    ostream = None
    if ns.output:
        ostream = open(ns.output, "wb")
    patchset.dump(stream=ostream)
    if ns.output:
        ostream.close()
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
