# -*- coding: utf-8 -*-

"""
***************************************************************************
    algorithm.py
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
import json


from qgis.core import (QgsProcessing,
                       QgsProviderRegistry,
                       QgsProcessingFeatureBasedAlgorithm,
                       QgsProcessingException,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterExtent,
                       QgsProcessingParameterCrs,
                       QgsProcessingParameterField,
                       QgsProcessingParameterString,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingOutputDefinition,
                       QgsCoordinateReferenceSystem,
                       QgsJsonExporter,
                       QgsJsonUtils,
                       QgsProcessingUtils)
from qgis.PyQt.QtCore import QCoreApplication, QDir, QTextCodec
from PyQt5.QtQml import QJSEngine

from processing.core.parameters import getParameterFromString
from processing_js.processing.outputs import create_output_from_string
from processing_js.processing.utils import JsUtils
from processing_js.gui.gui_utils import GuiUtils


class JsAlgorithm(QgsProcessingFeatureBasedAlgorithm):  # pylint: disable=too-many-public-methods
    """
    Javascript Algorithm
    """

    def __init__(self, description_file, script=None):
        super().__init__()

        self.script = script
        self.js_script = ''
        self.codec = None
        self.engine = None
        self.process_js_function = None
        self.json_exporter = None
        self.fields = None
        self._name = ''
        self._display_name = ''
        self._group = ''
        self.description_file = os.path.realpath(description_file) if description_file else None
        self.error = None
        self.commands = list()
        self.is_user_script = False
        if description_file:
            self.is_user_script = not description_file.startswith(JsUtils.builtin_scripts_folder())

        if self.script is not None:
            self.load_from_string()
        if self.description_file is not None:
            self.load_from_file()

    def createInstance(self):
        """
        Returns a new instance of this algorithm
        """
        if self.description_file is not None:
            return JsAlgorithm(self.description_file)

        return JsAlgorithm(description_file=None, script=self.script)

    def xxinitAlgorithm(self, _=None):
        """
        Initializes the algorithm
        """
        pass  # pylint: disable=unnecessary-pass

    def icon(self):
        """
        Returns the algorithm's icon
        """
        return GuiUtils.get_icon("providerJS.svg")

    def svgIconPath(self):
        """
        Returns a path to the algorithm's icon as a SVG file
        """
        return GuiUtils.get_icon_svg("providerJS.svg")

    def name(self):
        """
        Internal unique id for algorithm
        """
        return self._name

    def displayName(self):
        """
        User friendly display name
        """
        return self._display_name

    def shortDescription(self):
        """
        Returns the path to the script file, for use in toolbox tooltips
        """
        return self.description_file

    def group(self):
        """
        Returns the algorithm's group
        """
        return self._group

    def groupId(self):
        """
        Returns the algorithm's group ID
        """
        return self._group

    def load_from_string(self):
        """
        Load the algorithm from a string
        """
        lines = self.script.split('\n')
        self._name = 'unnamedalgorithm'
        self._display_name = self.tr('[Unnamed algorithm]')
        self.parse_script(iter(lines))

    def load_from_file(self):
        """
        Load the algorithm from a file
        """
        filename = os.path.basename(self.description_file)
        self._display_name = self._name
        self._name = filename[:filename.rfind('.')]
        self._display_name = self._name.replace('_', ' ')
        with open(self.description_file, 'r') as f:
            lines = [line.strip() for line in f]
        self.parse_script(iter(lines))

    def parse_script(self, lines):
        """
        Parse the lines from an JS script, initializing parameters and outputs as encountered
        """
        self.script = ''
        js_script_lines = list()
        self.error = None
        ender = 0
        line = next(lines).strip('\n').strip('\r')
        while ender < 10:
            if line.startswith('//#'):
                try:
                    self.process_metadata_line(line)
                except Exception:  # pylint: disable=broad-except
                    self.error = self.tr('This script has a syntax error.\n'
                                         'Problem with line: {0}').format(line)
            else:
                if line == '':
                    ender += 1
                else:
                    ender = 0
                js_script_lines.append(line)
            self.script += line + '\n'
            try:
                line = next(lines).strip('\n').strip('\r')
            except StopIteration:
                break
        self.js_script = '\n'.join(js_script_lines)

    def process_metadata_line(self, line):
        """
        Processes a "metadata" (##) line
        """
        line = line.replace('//#', '')

        # special commands
        #if line.lower().strip().startswith('dontuserasterpackage'):
        #    self.use_raster_package = False
        #    return

        value, type_ = self.split_tokens(line)
        if type_.lower().strip() == 'group':
            self._group = value
            return
        if type_.lower().strip() == 'name':
            self._name = self._display_name = value
            self._name = JsUtils.strip_special_characters(self._name.lower())
            return

        self.process_parameter_line(line)

    @staticmethod
    def split_tokens(line):
        """
        Attempts to split a line into tokens
        """
        tokens = line.split('=')
        return tokens[0], tokens[1]

    def process_parameter_line(self, line):
        """
        Processes a single script line representing a parameter
        """
        value, _ = self.split_tokens(line)
        description = JsUtils.create_descriptive_name(value)

        output = create_output_from_string(line)
        if output is not None:
            output.setName(value)
            output.setDescription(description)
            if issubclass(output.__class__, QgsProcessingOutputDefinition):
                self.addOutput(output)
            else:
                # destination type parameter
                self.addParameter(output)
        else:
            line = JsUtils.upgrade_parameter_line(line)
            param = getParameterFromString(line)
            if param is not None:
                self.addParameter(param)
            else:
                self.error = self.tr('This script has a syntax error.\n'
                                     'Problem with line: {0}').format(line)

    def outputFields(self, fields):
        self.fields = fields
        return self.fields

    def outputCrs(self, inputCrs):
        self.input_crs = inputCrs
        return QgsCoordinateReferenceSystem('EPSG:4326')

    def prepareAlgorithm(self, parameters, context, feedback):
        """
        Prepares the algorithm
        """
        self.engine = QJSEngine()
        js = """
        function process(feature)
        {
         return JSON.stringify(func(JSON.parse(feature)));
        }
        """

        for param in self.parameterDefinitions():
            if param.isDestination():
                continue

            if param.name() not in parameters or parameters[param.name()] is None:
                js += '{}=None;\n'.format(param.name())
                continue

            if isinstance(param,
                            (QgsProcessingParameterField, QgsProcessingParameterString, QgsProcessingParameterFile)):
                value = self.parameterAsString(parameters, param.name(), context)
                js += '{}="{}";'.format(param.name(), value)
            elif isinstance(param, QgsProcessingParameterNumber):
                value = self.parameterAsDouble(parameters, param.name(), context)
                js += '{}={};'.format(param.name(), value)

        js += self.js_script
        result = self.engine.evaluate(js)

        user_func = self.engine.globalObject().property("func")
        if not user_func:
            raise QgsProcessingException('No \'func\' function detected in script')
        if not user_func.isCallable():
            raise QgsProcessingException('Object \'func\' is not a callable function')

        self.process_js_function = self.engine.globalObject().property("process")
        self.json_exporter = QgsJsonExporter()

        self.codec = QTextCodec.codecForName("System")

        return True

    def outputName(self):
        return 'Processed'

    def processFeature(self, feature, context, feedback):
        """
        Executes the algorithm
        """
        self.json_exporter.setSourceCrs(self.input_crs)
        geojson = self.json_exporter.exportFeature(feature)
        res = self.process_js_function.call([geojson]).toVariant()
        if not res:
            return []

        return QgsJsonUtils.stringToFeatureList(res, self.fields, self.codec)

    def shortHelpString(self):
        """
        Returns the algorithms helper string
        """
        if self.description_file is None:
            return ''

        help_file = self.description_file + '.help'
        print(help_file)
        if os.path.exists(help_file):
            with open(help_file) as f:
                descriptions = json.load(f)

            return QgsProcessingUtils.formatHelpMapAsHtml(descriptions, self)

        return ''

    def tr(self, string, context=''):
        """
        Translates a string
        """
        if context == '':
            context = 'JsAlgorithmProvider'
        return QCoreApplication.translate(context, string)
