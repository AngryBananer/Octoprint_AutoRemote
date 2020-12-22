# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import requests
import json
from octoprint.events import Events

import os

class OctoAutoremotePlugin(octoprint.plugin.StartupPlugin,
                           octoprint.plugin.TemplatePlugin,
                           octoprint.plugin.SettingsPlugin,
                           octoprint.plugin.EventHandlerPlugin,
                           octoprint.plugin.ProgressPlugin):

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        if (hasattr, self._settings, 'autoremotekey'):
            #            self.autoremotekey = self._settings.get(["autoremotekey"])
            self._logger.info("Saving AutoRemote personal Key: %s" % self._settings.get(["autoremotekey"]))
        else:
            #            self.autoremotekey=''
            self._logger.info("No Autoremote Personal key set while trying to save!")

    def on_after_startup(self):
        self._logger.info("OctoAutoremote Plugin Active")
#        self.autoremotekey = self._settings.get(["autoremotekey"])
#        self._logger.debug("AutoRemote personal Key: %s" % self.autoremotekey)

    def get_settings_defaults(self):
        return dict(autoremotekey="",
                    autoremotesender="",
                    autoremotepassword="",
                    events=dict(Startup=False
                                    ,Shutdown=False
                                    ,ClientOpened=False
                                    ,ClientClosed=False
                                    ,ConnectivityChanged=False
                                    ,Connecting=False
                                    ,Connected=False
                                    ,PrintStarted=False
                                    ,Disconnecting=False
                                    ,Disconnected=False
                                    ,Error=False
                                    ,PrinterStateChanged=False
                                    ,Upload=False
                                    ,FileAdded=False
                                    ,FileRemoved=False
                                    ,FolderAdded=False
                                    ,FolderRemoved=False
                                    ,UpdatedFiles=False
                                    ,MetadataAnalysisStarted=False
                                    ,MetadataAnalysisFinished=False
                                    ,FileSelected=False
                                    ,FileDeselected=False
                                    ,TransferStarted=False
                                    ,TransferDone=False
                                    ,PrintFailed=False
                                    ,PrintCancelling=False
                                    ,PrintCancelled=False
                                    ,PrintPaused=False
                                    ,PrintResumed=False
                                    ,PrintDone=False
                                    ,MovieRendering=False
                                    ,MovieDone=False
                                    ,MovieFailed=False
                                    ,CaptureStart=False
                                    ,CaptureDone=False
                                    ,CaptureFailed=False
                                    ,SettingsUpdated=False
                                ),
                    PrintProgress=False,
                    PrintProgressSteps="5"
                    )

    def get_template_configs(self):
        return [dict(type="settings", name="AutoRemote", custom_bindings=False)]

    def get_assets(self):
        return dict(
            css=["css/octoautoremote.css"]
        )

    def get_settings_restricted_paths(self):
        # only used in OctoPrint versions > 1.2.16
        return dict(admin=[["autoremotekey"]])

######

    def on_print_progress(self, storage, path, progress):
        if self._settings.get(['PrintProgress']) and \
            progress % int(self._settings.get(['PrintProgressSteps'])) == 0 and \
            1 <= progress <= 99:
            #self._logger.info("PrintProgress: %s" % (progress))
            payload = {}
            payload['storage'] = storage
            payload['path'] = path
            payload['progress'] = str(progress)
            self.on_event(event='PrintProgress', payload=payload)

    def on_event(self, event, payload):
        events = self._settings.get(['events'], merged=True)

        if event in events and events[event] or event=='PrintProgress':
            messagedata = {}
            messagedata['event'] = event

            if not payload:
                payload = {}
                messagedata['nodata'] = 'No_Data_For_This_Event'
            else:
                for data in payload:
                    messagedata[str(data).lower()] = str(
                        payload[data]).replace("::ffff:", "")
                    self._logger.debug("forming_Message: '%s':'%s'" % (
                        str(data).lower(), str(payload[data]).replace("::ffff:", "")))

            message = 'OctoAutoremote=:=' + json.dumps(messagedata)

            self._logger.info("Calling Send: Event: %s, Message: %s" % (event, message))
            try:
                self._send_AutoRemote(message)
            except:
                self._logger.warning("Exception: Calling Send: Event: %s, Message: %s" % (event, message))
#        else:
#             self._logger.info("Event skipped: %s" % event)

    def _send_AutoRemote(self, message=",'nodata':'No_Data_For_This_Event'"):
        if self._settings.get(['autoremotekey']):

            import requests

            autoremotekey = self._settings.get(['autoremotekey'])
            autoremotesender = self._settings.get(['autoremotesender'])
            autoremotepassword = self._settings.get(['autoremotepassword'])

            url = "https://autoremotejoaomgcd.appspot.com/sendrequest"

            messageObj = {
                'message': message,
                'password': autoremotepassword,
                'sender': autoremotesender,
                'communication_base_params': {
                    'sender': autoremotesender,
                    'type': 'Message'
                }
            }

            dataObj = {
                'key': autoremotekey,
                'sender': autoremotesender,
                'request': json.dumps(messageObj)
            }

            self._logger.info("Sending %s to URL: %s" % (dataObj, url))

            try:
                res = requests.post(url, data=dataObj)
            except requests.exceptions.ConnectionError as e:
                self._logger.warning("ConnectionError %s while connecting to %s, check your connection!" % (e, url))
            except Exception as e:
                self._logger.warning("Error %s while: Sending %s to URL: %s" % (e, dataObj, url))
            else:
                if res.text == "OK":
                    self._logger.info("Response from %s: %s" % (url, res.text))
                else:
                    self._logger.warning("Response from %s: %s" % (url, res.text))
        else:
            self._logger.info("Your AutoRemote key is empty!")

    def get_update_information(self):
        return dict(
            OctoAutoremote=dict(
                displayName=self._plugin_name,
                displayVersion=self._plugin_version,
                type="github_release",
                current=self._plugin_version,
                user="AngryBananer",
                repo="Octoprint_AutoRemote",
                stable_branch=dict(branch="master", name="Stable"),
                pip="https://github.com/AngryBananer/Octoprint_Autoremote/archive/{target_version}.zip"
            )
        )

######


__plugin_name__ = "OctoAutoremote"
__plugin_implementation__ = OctoAutoremotePlugin()
__plugin_pythoncompat__ = ">=2.7,<4"

global __plugin_hooks__
__plugin_hooks__ = {
    "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
}
