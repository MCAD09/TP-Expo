$OS = lsb_release -i | cut -f 2-
if [$OS== "NixOS"] then
    nix-shell -p python310
else
    sudo apt install python310
fi

py -3.10 -m venv venv310
pip install mediapipe opencv-python pygame
