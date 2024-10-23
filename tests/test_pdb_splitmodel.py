#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 1118 João Pedro Rodrigues
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
Unit Tests for `pdb_splitmodel`.
"""

import os
import shutil
import sys
import tempfile
import unittest

from . import TestPDBTools, data_dir


class TestTool(TestPDBTools):
    """
    Generic class for testing tools.
    """

    name = 'zpdbtools.pdb_splitmodel'

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()  # set temp dir
        os.chdir(self.tempdir)

    def tearDown(self):
        os.chdir(os.path.dirname(os.path.abspath('.')))  # cd ../
        shutil.rmtree(self.tempdir)

    def test_default(self):
        """$ pdb_splitmodel data/ensemble_OK.pdb"""

        # Copy input file to tempdir

        # Simulate input
        src = os.path.join(data_dir, 'ensemble_OK.pdb')
        dst = os.path.join(self.tempdir, 'ensemble_OK.pdb')
        shutil.copy(src, dst)
        sys.argv = ['', dst]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)  # ensure the program exited OK.
        self.assertEqual(len(self.stdout), 0)  # no output
        self.assertEqual(len(self.stderr), 0)  # no errors

        # Read files created by script
        ofiles = [f for f in os.listdir(self.tempdir)
                  if f.startswith('ensemble_OK')]
        self.assertEqual(len(ofiles), 2 + 1)  # ori + 2 models

        for fpath in ofiles:
            if fpath == 'ensemble_OK.pdb':
                continue

            with open(os.path.join(self.tempdir, fpath), 'r') as handle:
                n_lines = len(handle.readlines())
                self.assertEqual(n_lines, 2)

    def test_run_iterable(self):
        """pdb_splitmodel.run(iterable)"""
        from zpdbtools import pdb_splitmodel

        # Copy input file to tempdir

        # Simulate input
        src = os.path.join(data_dir, 'ensemble_OK.pdb')
        dst = os.path.join(self.tempdir, 'ensemble_OK.pdb')
        shutil.copy(src, dst)

        with open(dst, 'r') as fin:
            lines = fin.readlines()

        pdb_splitmodel.run(lines)

        # Read files created by script
        ofiles = [f for f in os.listdir(self.tempdir)
                  if f.startswith('splitmodels')]
        self.assertEqual(len(ofiles), 2)

        for fpath in ofiles:
            if fpath == 'ensemble_OK.pdb':
                continue

            with open(os.path.join(self.tempdir, fpath), 'r') as handle:
                n_lines = len(handle.readlines())
                self.assertEqual(n_lines, 2)

    def test_run_iterable_with_name(self):
        """pdb_splitmodel.run(iterable)"""
        from zpdbtools import pdb_splitmodel

        # Copy input file to tempdir

        # Simulate input
        src = os.path.join(data_dir, 'ensemble_OK.pdb')
        dst = os.path.join(self.tempdir, 'ensemble_OK.pdb')
        shutil.copy(src, dst)

        with open(dst, 'r') as fin:
            lines = fin.readlines()

        pdb_splitmodel.run(lines, outname='newname')

        # Read files created by script
        ofiles = [f for f in os.listdir(self.tempdir)
                  if f.startswith('newname')]
        self.assertEqual(len(ofiles), 2)

        for fpath in ofiles:
            with open(os.path.join(self.tempdir, fpath), 'r') as handle:
                n_lines = len(handle.readlines())
                self.assertEqual(n_lines, 2)

    def test_run_fhandler(self):
        """pdb_splitmodel.run(fhandler)"""
        from zpdbtools import pdb_splitmodel

        # Copy input file to tempdir

        # Simulate input
        src = os.path.join(data_dir, 'ensemble_OK.pdb')
        dst = os.path.join(self.tempdir, 'ensemble_OK.pdb')
        shutil.copy(src, dst)

        with open(dst, 'r') as fin:
            pdb_splitmodel.run(fin)

        # Read files created by script
        ofiles = [f for f in os.listdir(self.tempdir)
                  if f.startswith('ensemble_OK')]
        self.assertEqual(len(ofiles), 2 + 1)  # ori + 2 models

        for fpath in ofiles:
            if fpath == 'ensemble_OK.pdb':
                continue

            with open(os.path.join(self.tempdir, fpath), 'r') as handle:
                n_lines = len(handle.readlines())
                self.assertEqual(n_lines, 2)

    def test_file_not_found(self):
        """$ pdb_splitmodel not_existing.pdb"""

        afile = os.path.join(data_dir, 'not_existing.pdb')
        sys.argv = ['', afile]

        self.exec_module()

        self.assertEqual(self.retcode, 1)  # exit code is 1 (error)
        self.assertEqual(len(self.stdout), 0)  # nothing written to stdout
        self.assertEqual(self.stderr[0][:22],
                         "ERROR!! File not found")  # proper error message

    @unittest.skipIf(os.getenv('SKIP_TTY_TESTS'), 'skip on GHA - no TTY')
    def test_file_missing(self):
        """$ pdb_splitmodel -10"""

        sys.argv = ['', '-10']

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)  # no output
        self.assertEqual(self.stderr[0][:38],
                         "ERROR!! File not found or not readable")

    @unittest.skipIf(os.getenv('SKIP_TTY_TESTS'), 'skip on GHA - no TTY')
    def test_helptext(self):
        """$ pdb_splitmodel"""

        sys.argv = ['']

        self.exec_module()

        self.assertEqual(self.retcode, 1)  # ensure the program exited gracefully.
        self.assertEqual(len(self.stdout), 0)  # no output
        self.assertEqual(self.stderr, self.module.__doc__.split("\n")[:-1])

    def test_invalid_option(self):
        """$ pdb_splitmodel -A data/ensemble_OK.pdb"""

        sys.argv = ['', '-A', os.path.join(data_dir, 'ensemble_OK.pdb')]

        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)
        self.assertEqual(self.stderr[0][:22],
                         "ERROR!! Script takes 1")  # proper error message
