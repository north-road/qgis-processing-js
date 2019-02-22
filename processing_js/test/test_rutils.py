# coding=utf-8
"""R Utils Test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = '(C) 2018 by Nyall Dawson'
__date__ = '20/04/2018'
__copyright__ = 'Copyright 2018, North Road'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import os
import unittest
from qgis.PyQt.QtCore import QCoreApplication, QSettings
from processing.core.ProcessingConfig import ProcessingConfig
from processing_js.processing.utils import JsUtils
from processing_js.processing.provider import JsAlgorithmProvider
from .utilities import get_qgis_app

QGIS_APP = get_qgis_app()


class RUtilsTest(unittest.TestCase):
    """Test RUtils work."""

    def __init__(self, methodName):
        """Run before all tests and set up environment"""
        super().__init__(methodName)

        # Don't mess with actual user settings
        QCoreApplication.setOrganizationName("North Road")
        QCoreApplication.setOrganizationDomain("qgis.org")
        QCoreApplication.setApplicationName("QGIS-R")
        QSettings().clear()

        # make Provider settings available
        self.provider = JsAlgorithmProvider()
        self.provider.load()

    def testBuiltInPath(self):
        """
        Tests built in scripts path
        """
        self.assertTrue(JsUtils.builtin_scripts_folder())
        self.assertIn('builtin_scripts', JsUtils.builtin_scripts_folder())
        self.assertTrue(os.path.exists(JsUtils.builtin_scripts_folder()))

    def testDefaultScriptsFolder(self):
        """
        Tests default user scripts folder
        """
        self.assertTrue(JsUtils.default_scripts_folder())
        self.assertIn('rscripts', JsUtils.default_scripts_folder())
        self.assertTrue(os.path.exists(JsUtils.default_scripts_folder()))

    def testScriptsFolders(self):
        """
        Test script folders
        """
        self.assertTrue(JsUtils.script_folders())
        self.assertIn(JsUtils.default_scripts_folder(), JsUtils.script_folders())
        self.assertIn(JsUtils.builtin_scripts_folder(), JsUtils.script_folders())

    def testDescriptiveName(self):
        """
        Tests creating descriptive name
        """
        self.assertEqual(JsUtils.create_descriptive_name('a B_4324_asd'), 'a B 4324 asd')

    def testStripSpecialCharacters(self):
        """
        Tests stripping special characters from a name
        """
        self.assertEqual(JsUtils.strip_special_characters('aB 43 24a:sd'), 'aB4324asd')

    def test_is_error_line(self):
        """
        Test is_error_line
        """
        self.assertFalse(JsUtils.is_error_line('xxx yyy'))
        self.assertTrue(JsUtils.is_error_line('Error something went wrong'))
        self.assertTrue(JsUtils.is_error_line('Execution halted'))


if __name__ == "__main__":
    suite = unittest.makeSuite(RUtilsTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
