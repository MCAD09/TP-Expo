$OS = lsb_release -i | cut -f 2-

if [$OS== "NixOS"] then
    nix-shell -p python310
    ghostty -e "./venv310/Scripts/activate"
else
    xfce4-terminal -x "./venv310/Scripts/activate"
fi