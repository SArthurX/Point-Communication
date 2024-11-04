import sys
import time

from pc_shell.console_defs import ConsoleDefs
from pc_shell.ui_manager import UiManager

major_version = 1
minor_version = 1
patch_version = 0

def print_welcome():
    print(ConsoleDefs.WELCOME_MSG + " - " +
          ConsoleDefs.VERSION_MSG.format(major_version, minor_version, patch_version))

if __name__ == '__main__':
    port_number = "COM3" 
    test_mode = False

    print_welcome()
    m_ui_manager = UiManager(port=port_number, test_mode=test_mode)
    m_ui_manager.launch()
    m_ui_manager.tracker_start_tracking_devices([]) 
    while m_ui_manager.active:
        time.sleep(1)
