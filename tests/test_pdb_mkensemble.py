#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 João Pedro Rodrigues
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
Unit Tests for `pdb_mkensemble`.
"""

import os
import sys
import unittest

from . import TestPDBTools, data_dir


class TestTool(TestPDBTools):
    """
    Generic class for testing tools.
    """

    name = 'zpdbtools.pdb_mkensemble'

    def test_default(self):
        """$ pdb_mkensemble data/dummy.pdb"""

        # Simulate input
        sys.argv = ['', os.path.join(data_dir, 'dummy.pdb'),
                    os.path.join(data_dir, 'dummy.pdb')]

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 385)
        self.assertEqual(len(self.stderr), 0)

    def test_default_multiple(self):
        """$ pdb_mkensemble data/dummy.pdb x20"""

        # Simulate input
        args = [os.path.join(data_dir, 'dummy.pdb') for _ in range(20)]
        sys.argv = [''] + args

        # Execute the script
        self.exec_module()

        # Validate results
        self.assertEqual(self.retcode, 0)
        self.assertEqual(len(self.stdout), 3823)
        self.assertEqual(len(self.stderr), 0)

        # Validate MODEL lines
        model_no = [
            int(line[10:14])
            for line in self.stdout
            if line.startswith('MODEL')
        ]
        model_no = sorted(set(model_no))
        n_models = len(model_no)
        self.assertEqual(n_models, 20)
        self.assertEqual(model_no, list(range(1, 21)))

    def test_file_not_found(self):
        """$ pdb_mkensemble not_existing.pdb"""

        # Error (file not found)
        afile = os.path.join(data_dir, 'not_existing.pdb')
        sys.argv = ['', afile]

        # Execute the script
        self.exec_module()

        self.assertEqual(self.retcode, 1)  # exit code is 1 (error)
        self.assertEqual(len(self.stdout), 0)  # nothing written to stdout
        self.assertEqual(self.stderr[0][:22],
                         "ERROR!! File not found")  # proper error message

    @unittest.skipIf(os.getenv('SKIP_TTY_TESTS'), 'skip on GHA - no TTY')
    def test_helptext(self):
        """$ pdb_mkensemble"""

        sys.argv = ['']

        # Execute the script
        self.exec_module()

        self.assertEqual(self.retcode, 1)
        self.assertEqual(len(self.stdout), 0)  # no output
        self.assertEqual(self.stderr, self.module.__doc__.split("\n")[:-1])
