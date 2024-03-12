# coding=utf-8
from __future__ import absolute_import

__author__ = "usr577 <beneoesdorfg@gmail.com>"
__license__ = "GNU Affero General Public License http://www.gnu.org/licenses/agpl.html"
__copyright__ = "Copyright (C) 2021 Shawn Bruce - Released under terms of the AGPLv3 License"

import octoprint.plugin
import requests
import xml.etree.ElementTree as ET

class PSUControl_Raspberrymatic(octoprint.plugin.StartupPlugin,
                         octoprint.plugin.RestartNeedingPlugin,
                         octoprint.plugin.TemplatePlugin,
                         octoprint.plugin.SettingsPlugin):

    def __init__(self):
        self.config = dict()

        self._configuredGPIOPins = []


    def get_settings_defaults(self):
        return dict(
            ip = 'None',
            onCommand = 'None',
            offCommand = 'None',
            senseCommand = 'None',
        )


    def on_settings_initialized(self):
        self.reload_settings()

    def reload_settings(self):
        for k, v in self.get_settings_defaults().items():
            if type(v) == str:
                v = self._settings.get([k])
            elif type(v) == int:
                v = self._settings.get_int([k])
            elif type(v) == float:
                v = self._settings.get_float([k])
            elif type(v) == bool:
                v = self._settings.get_boolean([k])

            self.config[k] = v
            self._logger.debug("{}: {}".format(k, v))


    def on_startup(self, host, port):
        psucontrol_helpers = self._plugin_manager.get_helpers("psucontrol")
        if not psucontrol_helpers or 'register_plugin' not in psucontrol_helpers.keys():
            self._logger.warning("The version of PSUControl that is installed does not support plugin registration.")
            return

        self._logger.debug("Registering plugin with PSUControl")
        psucontrol_helpers['register_plugin'](self)

    def turn_psu_on(self):
        if self.config['onCommand'] == 'None' or self.config['offCommand'] == 'None' or self.config['ip'] == 'None':
            self._logger.warning("Switching is not enabled")
            return
        try:
            requests.get(self.config['ip'] + self.config['onCommand'])
        except Exception:
            self._logger.exception("Exception while Switching")




    def turn_psu_off(self):
        if self.config['offCommand'] == 'None' or self.config['onCommand'] == 'None' or self.config['ip'] == 'None':
            self._logger.warning("Switching is not enabled")
            return
        try:
            requests.get(self.config['ip'] + self.config['offCommand'])
        except Exception:
            self._logger.exception("Exception while Switching")


    def get_psu_state(self):
        if self.config['senseCommand'] == 'None' or self.config['ip'] == 'None':
            self._logger.warning("Sensing is not enabled")
            return 0

        r = 0
        try:
            r = ET.fromstring(requests.get(self.config['ip'] + self.config['senseCommand']).text).find("datapoint").get("value")
        except Exception:
            self._logger.exception("Exception while reading State")
            return False
        self._logger.debug("Result: {}".format(r))
        r = bool(r)

        return r


    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self.reload_settings()

    def get_settings_version(self):
        return 1


    def on_settings_migrate(self, target, current=None):
        pass


    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=False)
        ]


    def get_update_information(self):
        return dict(
            psucontrol_raspberrymatic=dict(
                displayName="PSU Control - Raspberrymatic",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="usr577",
                repo="OctoPrint-PSUControl-RPiGPIO",
                current=self._plugin_version,

                # update method: pip w/ dependency links
                pip="https://github.com/usr577/OctoPrint-PSUControl-RPiGPIO/archive/{target_version}.zip"
            )
        )


    # < Holdovers from initial release. Will be removed later.
    def setup(self, *args, **kwargs):
        pass

    def cleanup(self, *args, **kwargs):
        pass
    # >

__plugin_name__ = "PSU Control - Raspberrymatic"
__plugin_pythoncompat__ = ">=2.7,<4"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = PSUControl_Raspberrymatic()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
