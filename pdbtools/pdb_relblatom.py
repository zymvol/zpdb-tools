#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2024 Zymvol
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Re-label atoms based on integer count.

Usage:
    python pdb_relblatom.py <pdb file>

Example:
    python pdb_relblatom.py 1CTF.pdb

This program is part of the `pdb-tools` suite of utilities and should not be
distributed isolatedly. The `pdb-tools` were created to quickly manipulate PDB
files using the terminal, and can be used sequentially, with one tool streaming
data to another.
"""
import sys
import os
from collections import Counter
from itertools import cycle


__author__ = "Joao MC Teixeira"
__email__ = "jteixeira@zymvol.com"


def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options.
    """

    # Defaults
    fh = sys.stdin  # file handle

    if not len(args):
        # Reading from pipe
        if sys.stdin.isatty():
            sys.stderr.write(__doc__)
            sys.exit(1)

    elif len(args) == 1:
        # Reading from file
        if not os.path.isfile(args[0]):
            emsg = 'ERROR!! File not found or not readable: \'{}\'\n'
            sys.stderr.write(emsg.format(args[0]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        fh = open(args[0], 'r')

    else:  # Whatever ...
        emsg = 'ERROR!! Script takes 1 argument, not \'{}\'\n'
        sys.stderr.write(emsg.format(len(args)))
        sys.stderr.write(__doc__)
        sys.exit(1)

    return fh


def run(lines):
    """
    Re-label atoms based on integer count.

    Integer count is restarted on each residue.

    Parameters
    ----------
    lines : iterable over lines
    """
    prev_res = None
    for line in lines:

        if line.startswith(('ATOM', 'HETATM')):

            res_code = (line[17:20], line[22:26])

            if res_code != prev_res:
                c = Counter()

            atom_name = line[12:16]

            c[atom_name] += 1

            atom_number = cycle(str(c[atom_name]).ljust(4))

            new_atom_number = ''.join(
                atom_name[i] if atom_name[i] != ' ' else next(atom_number)
                for i in range(len(atom_name))
                )

            yield line[:12] + new_atom_number + line[16:]

            prev_res = res_code
            prev_atom_number = new_atom_number

        elif line.startswith('ANISOU'):

            res_code = (line[17:20], line[22:26])

            if new_atom_number is None or res_code != prev_res:
                raise ValueError(
                    'ANISOU line provided before ATOM line. '
                    'Cannot re-label atom.'
                    )

            yield line[:12] + prev_atom_number + line[16:]
            new_atom_number = None

        else:
            yield line


pdb_relblatom = run


def main():
    # Check Input
    pdbfh = check_input(sys.argv[1:])

    # Do the job
    new_pdb = run(pdbfh)

    try:
        _buffer = []
        _buffer_size = 5000  # write N lines at a time
        for lineno, line in enumerate(new_pdb):
            if not (lineno % _buffer_size):
                sys.stdout.write(''.join(_buffer))
                _buffer = []
            _buffer.append(line)

        sys.stdout.write(''.join(_buffer))
        sys.stdout.flush()
    except IOError:
        # This is here to catch Broken Pipes
        # for example to use 'head' or 'tail' without
        # the error message showing up
        pass

    sys.exit(0)


if __name__ == '__main__':
    main()
