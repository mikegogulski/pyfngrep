#!/usr/bin/env python
#
# Find strings/regexes in Python source files, annotating with the function
# or class.method where they occur.
from argparse import ArgumentParser
import os
from pathlib import Path
import re
from typing import List


def fn_or_class_name(s: str) -> str:
    """
    Given a line of Python source code that either starts with `class` or
    `def`, or starts with an indented `def` return the name of the class or
    function scope the subsequent lines belong to.

    TODO: Expand to handling defs-within-defs, nested classes, etc.
    """
    return s.split()[1].split('(')[0]


def _pyfngrep(
    regex: str, paths: List[str], base: str, ignore_case: bool = False
) -> None:
    """
    The core thingy.

    :param regex: string/regex to match
    :param paths: list of paths to try, as strings
    :param base: base part of each path, which can be stripped off
    :param ignore_case: use `re.IGNORECASE` for pattern matching if True

    TODO: options for "print def name only", "print filename only", etc.
    """
    re_flags = re.I if ignore_case else 0
    for p in paths:
        curcls, curfn, lineno = None, None, 0
        rel_p = p[len(base):]
        lines = [line.strip('\n') for line in open(p).readlines()]
        for line in lines:
            lineno += 1
            if line.startswith('class '):
                curcls = fn_or_class_name(line)
                curfn = None
            if (
                not curcls
                and line.startswith('def ')
                or curcls
                and re.match(r'^ +def ', line)
            ):
                curfn = fn_or_class_name(line)
            if not curcls and len(line.strip()) == 0:
                curfn = None
            if re.search(regex, line, flags=re_flags):
                relevant = line.lstrip()
                if curcls:
                    print(f'{rel_p}:{lineno}:{curcls}.{curfn}(): {relevant}')
                else:
                    print(f'{rel_p}:{lineno}:{curfn}(): {relevant}')


def get_paths(p: str) -> List[str]:
    """
    Recurse through a directory path and return a list of all Python source
    code files (.py and .pyi).

    :param p: directory path to recurse over
    :return: list of full (relative) paths to .py and .pyi files
    """
    ret = list()
    for root, _, files in os.walk(p):
        for f in files:
            if f.endswith('.py') or f.endswith('.pyi'):
                ret.append(os.path.join(root, f))
    return ret


def pyfngrep(regex: str, pathspec: str, ignore_case: bool = False) -> None:
    """
    Helper function to handle converting requests for single files to a list
    containing a path to that single file.

    :param regex: string/regex to match
    :param pathspec: filename or list of paths to try, as strings
    :param ignore_case: use `re.IGNORECASE` for pattern matching if True
    """
    if Path(path).is_file():
        return _pyfngrep(regex, [pathspec], '', ignore_case)
    return _pyfngrep(regex, get_paths(pathspec), pathspec, ignore_case)


if __name__ == '__main__':
    p = ArgumentParser(
        description='Find the specified string/regex in Python source files'
    )
    p.add_argument(
        '-i',
        '--ignore-case',
        action='store_true',
        help='Ignore case. Default false.',
    )
    p.add_argument(
        'regex',
        type=str,
        nargs=1,
        help='String or regex pattern to search for',
    )
    p.add_argument(
        'path',
        type=str,
        nargs=1,
        help='File or directory to search (recursively)',
    )
    args = p.parse_args()
    ignore_case = args.ignore_case
    regex = args.regex[0]
    path = args.path[0]
    pyfngrep(regex, path, ignore_case)
