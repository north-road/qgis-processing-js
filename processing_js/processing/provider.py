# -*- coding: utf-8 -*-

"""
***************************************************************************
    provider.py
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
from qgis.core import (Qgis,
                       QgsProcessingProvider,
                       QgsMessageLog)

from processing.core.ProcessingConfig import ProcessingConfig, Setting
from processing.gui.ProviderActions import (ProviderActions,
                                            ProviderContextMenuActions)

from processing_js.processing.actions.create_new_script import CreateNewScriptAction
from processing_js.processing.actions.edit_script import EditScriptAction
from processing_js.processing.actions.delete_script import DeleteScriptAction
from processing_js.processing.exceptions import InvalidScriptException
from processing_js.processing.utils import JsUtils
from processing_js.processing.algorithm import JsAlgorithm
from processing_js.gui.gui_utils import GuiUtils


class JsAlgorithmProvider(QgsProcessingProvider):
    """
    Processing provider for executing Javascript scripts
    """

    def __init__(self):
        super().__init__()
        self.algs = []
        self.actions = []
        create_script_action = CreateNewScriptAction()
        self.actions.append(create_script_action)
        self.contextMenuActions = [EditScriptAction(),
                                   DeleteScriptAction()]

    def load(self):
        """
        Called when first loading provider
        """
        ProcessingConfig.settingIcons[self.name()] = self.icon()
        ProcessingConfig.addSetting(Setting(
            self.name(), JsUtils.SCRIPTS_FOLDER,
            self.tr('Javascript scripts folder'), JsUtils.default_scripts_folder(),
            valuetype=Setting.MULTIPLE_FOLDERS))

        ProviderActions.registerProviderActions(self, self.actions)
        ProviderContextMenuActions.registerProviderContextMenuActions(self.contextMenuActions)
        ProcessingConfig.readSettings()
        self.refreshAlgorithms()
        return True

    def unload(self):
        """
        Called when unloading provider
        """
        ProcessingConfig.removeSetting(JsUtils.SCRIPTS_FOLDER)
        ProviderActions.deregisterProviderActions(self)
        ProviderContextMenuActions.deregisterProviderContextMenuActions(self.contextMenuActions)

    def isActive(self):
        """
        Returns True if provider is active
        """
        return True

    def setActive(self, active):
        """
        Sets whether the provider should be activated
        """
        pass

    def icon(self):
        """
        Returns the provider's icon
        """
        return GuiUtils.get_icon("providerJS.svg")

    def svgIconPath(self):
        """
        Returns a path to the provider's icon as a SVG file
        """
        return GuiUtils.get_icon_svg("providerJS.svg")

    def name(self):
        """
        Display name for provider
        """
        return self.tr('Javascript')

    def id(self):
        """
        Unique ID for provider
        """
        return 'js'

    def loadAlgorithms(self):
        """
        Called when provider must populate its available algorithms
        """
        algs = []
        for f in JsUtils.script_folders():
            algs.extend(self.load_scripts_from_folder(f))

        for a in algs:
            self.addAlgorithm(a)

    def load_scripts_from_folder(self, folder):
        """
        Loads all scripts found under the specified sub-folder
        """
        if not os.path.exists(folder):
            return []

        algs = []
        for path, _, files in os.walk(folder):
            for description_file in files:
                if description_file.lower().endswith('js'):
                    try:
                        fullpath = os.path.join(path, description_file)
                        alg = JsAlgorithm(fullpath)
                        if alg.name().strip():
                            algs.append(alg)
                    except InvalidScriptException as e:
                        QgsMessageLog.logMessage(e.msg, self.tr('Processing'), Qgis.Critical)
                    except Exception as e:  # pylint: disable=broad-except
                        QgsMessageLog.logMessage(
                            self.tr('Could not load Javascript script: {0}\n{1}').format(description_file, str(e)),
                            self.tr('Processing'), Qgis.Critical)
        return algs

    def tr(self, string, context=''):
        """
        Translates a string
        """
        if context == '':
            context = 'JsAlgorithmProvider'
        return QCoreApplication.translate(context, string)
