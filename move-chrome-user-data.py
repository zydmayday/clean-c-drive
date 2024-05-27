import os
import shutil
import subprocess
import ctypes
from pathlib import Path

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def close_chrome():
    subprocess.call(["taskkill", "/F", "/IM", "chrome.exe"])

def get_chrome_user_data_dir():
    local_app_data = os.getenv('LOCALAPPDATA')
    chrome_user_data_dir = Path(local_app_data) / 'Google' / 'Chrome' / 'User Data'
    return chrome_user_data_dir

def copy_user_data(src, dst):
    if not dst.exists():
        shutil.copytree(src, dst)
    else:
        print("Destination folder already exists. Aborting copy to avoid data loss.")
        exit(1)

def modify_shortcut(new_user_data_dir):
    desktop = Path(os.getenv('USERPROFILE')) / 'Desktop'
    for item in desktop.iterdir():
        if item.suffix == '.lnk' and 'chrome' in item.name.lower():
            shortcut_path = str(item)
            target = shortcut_path.replace('"', '')  # Ensure target path has no quotes
            target += f' --user-data-dir="{new_user_data_dir}"'
            
            # Use Powershell to update the shortcut target
            subprocess.call([
                'powershell', '-ExecutionPolicy', 'Bypass',
                '-Command', f'$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut("{shortcut_path}"); $Shortcut.TargetPath = "{target}"; $Shortcut.Save()'
            ])
            print(f"Modified shortcut: {shortcut_path}")

def main():
    if not is_admin():
        print("This script requires administrative privileges. Please run it as an administrator.")
        return

    close_chrome()

    user_data_dir = get_chrome_user_data_dir()
    if not user_data_dir.exists():
        print("Chrome user data directory not found.")
        return

    new_user_data_dir = input("Enter the new user data directory (e.g., D:\\Chrome\\User Data): ")
    new_user_data_dir = Path(new_user_data_dir)

    copy_user_data(user_data_dir, new_user_data_dir)
    modify_shortcut(new_user_data_dir)

    print("Chrome user data directory moved successfully. Please restart Chrome using the modified shortcut.")

if __name__ == "__main__":
    main()
