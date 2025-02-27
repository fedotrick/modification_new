import os
import winshell
from win32com.client import Dispatch

def create_shortcut():
    desktop = winshell.desktop()
    path = os.path.join(desktop, "Контроль качества отливок.lnk")
    target = os.path.abspath("dist/CastingQualityControl.exe")
    
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.IconLocation = os.path.abspath("app.ico")
    shortcut.save()

if __name__ == '__main__':
    create_shortcut() 