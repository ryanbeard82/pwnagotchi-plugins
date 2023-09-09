# display-password shows recently cracked passwords on the pwnagotchi display 
#
#
###############################################################
#
# Inspired by, and code shamelessly yoinked from
# the pwnagotchi memtemp.py plugin by https://github.com/xenDE
#
###############################################################
#
# Updated 9/8/23 by Ryan Beard
#
# Moved several params to config.toml and refactored the code
# Added functions to hide password when peers are detected
# Hat tip to @highrup on Reddit: https://www.reddit.com/r/pwnagotchi/comments/16c2h2o/dev_question/
#
# Requires the following config elements:
#
#     main.plugins.display-password.enabled = [bool] / true
#     main.plugins.display-password.pw_x_coord = [int] / 0
#     main.plugins.display-password.pw_y_coord = [int] / 95
#
###############################################################

import os
import logging

import pwnagotchi
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts

from os.path import getsize
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK


class DisplayPassword(plugins.Plugin):
    __author__ = '@nagy_craig'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'A plugin to display recently cracked passwords'

    def __init__(self):
        self.peers_detected = False # Initialize peers_detected as False

    def on_loaded(self):
        logging.info("display-password loaded")

    def on_ui_setup(self, ui):
        pw_pos = (int(self.options["pw_x_coord"]),int(self.options["pw_y_coord"]))

        ui.add_element('display-password', LabeledValue(color=BLACK, label='', value='',
                                                position=pw_pos,
                                                label_font=fonts.Bold, text_font=fonts.Small))

    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element('display-password')

    def on_ui_update(self, ui):
        
        # If peers are detected, clear the display or set a message.
        if self.peers_detected:
            ui.set('display-password', '') # Clear the display or set a message if desired
            logging.info("Not displaying cracked password because peers are detected.")
            return
        
        if os.path.getsize('/root/handshakes/wpa-sec.cracked.potfile') == 0:
            ui.set('display-password', "Nothing to see here...")
        else:
            last_line = 'tail -n 1 /root/handshakes/wpa-sec.cracked.potfile | awk -F: \'{print $3 " - " $4}\''
            ui.set('display-password', "%s" % (os.popen(last_line).read().rstrip()))
    
    # Called when a new peer is detected
    def on_peer_detected(self, agent, peer):
        self.peers_detected = True
        logging.info("Peer detected: %s", peer)

    # Called when a known peer is lost
    def on_peer_lost(self, agent, peer):
        self.peers_detected = False
        logging.info("Peer lost: %s", peer)