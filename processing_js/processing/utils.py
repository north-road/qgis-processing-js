# -*- coding: utf-8 -*-

"""
***************************************************************************
    utils.py
    ---------------------
    Date                 : August 2012
    Copyright            : (C) 2012 by Victor Olaya
    Email                : volayaf at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
import os

from qgis.PyQt.QtCore import QCoreApplication
from processing.core.ProcessingConfig import ProcessingConfig
from processing.tools.system import userFolder, mkdir

DEBUG = True


class JsUtils:  # pylint: disable=too-many-public-methods
    """
    Utilities for the Javascript Provider and Algorithm
    """

    SCRIPTS_FOLDER = 'SCRIPTS_FOLDER'

    VALID_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    @staticmethod
    def builtin_scripts_folder():
        """
        Returns the built-in scripts path
        """
        return os.path.join(os.path.dirname(__file__), '..', 'builtin_scripts')

    @staticmethod
    def default_scripts_folder():
        """
        Returns the default path to look for user scripts within
        """
        folder = os.path.join(userFolder(), 'jsscripts')
        mkdir(folder)
        return os.path.abspath(folder)

    @staticmethod
    def script_folders():
        """
        Returns a list of folders to search for scripts within
        """
        folder = ProcessingConfig.getSetting(JsUtils.SCRIPTS_FOLDER)
        if folder is not None:
            folders = folder.split(';')
        else:
            folders = [JsUtils.default_scripts_folder()]

        folders.append(JsUtils.builtin_scripts_folder())
        return folders

    @staticmethod
    def create_descriptive_name(name):
        """
        Returns a safe version of a parameter name
        """
        return name.replace('_', ' ')

    @staticmethod
    def strip_special_characters(name):
        """
        Strips non-alphanumeric characters from a name
        """
        return ''.join(c for c in name if c in JsUtils.VALID_CHARS)

    @staticmethod
    def is_error_line(line):
        """
        Returns True if the given line looks like an error message
        """
        return any([l in line for l in ['Error ', 'Execution halted']])

    @staticmethod
    def html_formatted_console_output(output):
        """
        Returns a HTML formatted string of the given output lines
        """
        s = '<h2>{}</h2>\n'.format(JsUtils.tr('R Output'))
        s += '<code>\n'
        for line in output:
            s += '{}<br />\n'.format(line)
        s += '</code>'
        return s

    @staticmethod
    def upgrade_parameter_line(line: str) -> str:
        """
        Upgrades a parameter definition line from 2.x to 3.x format
        """
        # alias 'selection' to 'enum'
        if '=selection' in line:
            line = line.replace('=selection', '=enum')
        return line

    @staticmethod
    def tr(string, context=''):
        """
        Translates a string
        """
        if context == '':
            context = 'RUtils'
        return QCoreApplication.translate(context, string)
