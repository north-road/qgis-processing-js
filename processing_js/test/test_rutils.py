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

    def test_is_windows(self):
        """
        Test is_windows
        """
        self.assertFalse(JsUtils.is_windows())  # suck it, Windows users!

    def test_is_macos(self):
        """
        Test is_macos
        """
        self.assertFalse(JsUtils.is_macos())  # suck it even more, MacOS users!

    def test_guess_r_binary_folder(self):
        """
        Test guessing the R binary folder -- not much to do here, all the logic is Windows specific
        """
        self.assertFalse(JsUtils.guess_r_binary_folder())

    def test_r_binary_folder(self):
        """
        Test retrieving R binary folder
        """
        self.assertFalse(JsUtils.r_binary_folder())
        ProcessingConfig.setSettingValue(JsUtils.R_FOLDER, '/usr/local/bin')
        self.assertEqual(JsUtils.r_binary_folder(), '/usr/local/bin')
        ProcessingConfig.setSettingValue(JsUtils.R_FOLDER, None)
        self.assertFalse(JsUtils.r_binary_folder())

    def test_r_executable(self):
        """
        Test retrieving R executable
        """
        self.assertEqual(JsUtils.path_to_r_executable(), 'R')
        self.assertEqual(JsUtils.path_to_r_executable(script_executable=True), 'Rscript')
        ProcessingConfig.setSettingValue(JsUtils.R_FOLDER, '/usr/local/bin')
        self.assertEqual(JsUtils.path_to_r_executable(), '/usr/local/bin/R')
        self.assertEqual(JsUtils.path_to_r_executable(script_executable=True), '/usr/local/bin/Rscript')
        ProcessingConfig.setSettingValue(JsUtils.R_FOLDER, None)
        self.assertEqual(JsUtils.path_to_r_executable(), 'R')
        self.assertEqual(JsUtils.path_to_r_executable(script_executable=True), 'Rscript')

    def test_package_repo(self):
        """
        Test retrieving/setting the package repo
        """
        self.assertEqual(JsUtils.package_repo(), 'http://cran.at.r-project.org/')
        ProcessingConfig.setSettingValue(JsUtils.R_REPO, 'http://mirror.at.r-project.org/')
        self.assertEqual(JsUtils.package_repo(), 'http://mirror.at.r-project.org/')
        ProcessingConfig.setSettingValue(JsUtils.R_REPO, 'http://cran.at.r-project.org/')
        self.assertEqual(JsUtils.package_repo(), 'http://cran.at.r-project.org/')

    def test_use_user_library(self):
        """
        Test retrieving/setting the user library setting
        """
        self.assertTrue(JsUtils.use_user_library())
        ProcessingConfig.setSettingValue(JsUtils.R_USE_USER_LIB, False)
        self.assertFalse(JsUtils.use_user_library())
        ProcessingConfig.setSettingValue(JsUtils.R_USE_USER_LIB, True)
        self.assertTrue(JsUtils.use_user_library())

    def test_library_folder(self):
        """
        Test retrieving/setting the library folder
        """
        self.assertIn('/profiles/default/processing/rlibs', JsUtils.r_library_folder())
        ProcessingConfig.setSettingValue(JsUtils.R_LIBS_USER, '/usr/local')
        self.assertEqual(JsUtils.r_library_folder(), '/usr/local')
        ProcessingConfig.setSettingValue(JsUtils.R_LIBS_USER, None)
        self.assertIn('/profiles/default/processing/rlibs', JsUtils.r_library_folder())

    def test_is_error_line(self):
        """
        Test is_error_line
        """
        self.assertFalse(JsUtils.is_error_line('xxx yyy'))
        self.assertTrue(JsUtils.is_error_line('Error something went wrong'))
        self.assertTrue(JsUtils.is_error_line('Execution halted'))

    def test_r_is_installed(self):
        """
        Test checking that R is installed
        """
        self.assertIsNone(JsUtils.check_r_is_installed())
        ProcessingConfig.setSettingValue(JsUtils.R_FOLDER, '/home')
        self.assertTrue(JsUtils.check_r_is_installed())
        self.assertIn('R is not installed', JsUtils.check_r_is_installed())
        ProcessingConfig.setSettingValue(JsUtils.R_FOLDER, None)
        self.assertIsNone(JsUtils.check_r_is_installed())


if __name__ == "__main__":
    suite = unittest.makeSuite(RUtilsTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
