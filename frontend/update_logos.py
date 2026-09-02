import os
import shutil

source_image = r"C:\Users\Shanur\.gemini\antigravity-ide\brain\66d9003b-088c-462f-8b91-235aa0733e40\.user_uploaded\media_1788380907501.jpg"
public_logo = r"c:\Users\Shanur\OneDrive\Desktop\Impactverse\github-repo\frontend\public\logo.jpg"
res_dir = r"c:\Users\Shanur\OneDrive\Desktop\Impactverse\github-repo\frontend\android\app\src\main\res"

# 1. Update UI Logo
shutil.copyfile(source_image, public_logo)
print("Updated UI Logo")

# 2. Update APK Launcher Icons
for folder in os.listdir(res_dir):
    if folder.startswith("mipmap-"):
        folder_path = os.path.join(res_dir, folder)
        for icon_name in ["ic_launcher.png", "ic_launcher_round.png", "ic_launcher_foreground.png"]:
            icon_path = os.path.join(folder_path, icon_name)
            if os.path.exists(icon_path):
                # Copy the new JPG over the PNG (Android handles this fine usually, 
                # but renaming it to .png extension just to match the reference).
                shutil.copyfile(source_image, icon_path)
                print(f"Replaced {icon_path}")

print("Done updating APK icons.")
