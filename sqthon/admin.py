import os, sys
from typing import List, Tuple
import traceback
import win32api, win32con, win32event, win32process
from win32com.shell.shell import ShellExecuteEx
import win32com.shell.shellcon as shellcon

# This script going to run on windows only. (for now)

def is_admin():
    if os.name == "nt":
        import ctypes
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            traceback.print_exc()
            return False


def runAsAdmin(service: str, action: str):
    cmd = "sc"
    params = f"{action} {service}"
    execute_cmd = ShellExecuteEx(
        lpVerb="runas",
        lpFile=cmd,
        lpParameters=params,
        fMask=shellcon.SEE_MASK_NOCLOSEPROCESS
    )

    if execute_cmd:
        handle = execute_cmd["hProcess"]
        win32event.WaitForSingleObject(handle, win32event.INFINITE)

        exit_code = win32process.GetExitCodeProcess(handle)
        print(f"Process exited with code: {exit_code}")

        if exit_code == 0:
            if action == "start":
                print(f"{service} server instance started successfully.")
            elif action == "stop":
                print(f"{service} server instance stopped successfully.")
            return True
        else:
            if action == "start":
                print(f"Failed to start the {service} server. Exit code: {exit_code}")
            elif action == "stop":
                print(f"Failed to stop the {service} server. Exit code: {exit_code}")
    else:
        if action == "start":
            print(f"Failed to start {service} server instance.")
        elif action == "stop":
            print(f"Failed to stop the {service} server instance.")

