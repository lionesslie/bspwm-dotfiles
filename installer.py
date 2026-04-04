#!/usr/bin/env python3
"""
bspwm-dotfiles installer
Installs packages and copies config files to ~/.config.
Source: https://github.com/lionesslie/bspwm-dotfiles
"""

import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path

# ── Colors ────────────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def info(msg):   print(f"{CYAN}[*]{RESET} {msg}")
def ok(msg):     print(f"{GREEN}[✓]{RESET} {msg}")
def warn(msg):   print(f"{YELLOW}[!]{RESET} {msg}")
def error(msg):  print(f"{RED}[✗]{RESET} {msg}")
def header(msg): print(f"\n{BOLD}{CYAN}{'─'*50}{RESET}\n{BOLD}  {msg}{RESET}\n{BOLD}{CYAN}{'─'*50}{RESET}")

# ── Package list ──────────────────────────────────────────────────────────────
PACMAN_PACKAGES = [
    "bspwm", "sxhkd",
    "polybar", "picom", "dunst",
    "kitty", "rofi", "thunar",
    "fish", "feh", "udiskie", "udisks2",
    "alsa-utils",
    "xorg-xrandr", "xorg-xinput", "xorg-setxkbmap", "xorg-xset",
    "ttf-jetbrains-mono-nerd", "ttf-material-design-icons-extended",
    "papirus-icon-theme",
    "playerctl", "brightnessctl", "networkmanager",
    "libnotify", "xclip", "flameshot", "firefox",
    "neovim",
    "base-devel",
    "steam", "gamemode",
]

# ── Repo ──────────────────────────────────────────────────────────────────────
REPO_URL = "https://github.com/lionesslie/bspwm-dotfiles"

# repo folder → ~/.config/target
CONFIG_MAP = {
    "bspwm":   "bspwm",
    "sxhkd":   "sxhkd",
    "polybar":  "polybar",
    "picom":    "picom",
    "dunst":    "dunst",
    "kitty":    "kitty",
    "rofi":     "rofi",
    "fish":     "fish",
    "nvim":     "nvim",
}

# ─────────────────────────────────────────────────────────────────────────────

def run(cmd, check=True, capture=False):
    return subprocess.run(
        cmd, shell=True, check=check,
        capture_output=capture, text=True
    )

def is_arch():
    return shutil.which("pacman") is not None

def install_packages():
    header("Installing Packages")

    if not is_arch():
        error("This installer only supports Arch Linux (pacman).")
        sys.exit(1)

    already, missing = [], []
    for pkg in PACMAN_PACKAGES:
        result = run(f"pacman -Qi {pkg}", check=False, capture=True)
        if result.returncode == 0:
            already.append(pkg)
        else:
            missing.append(pkg)

    if already:
        ok(f"Already installed ({len(already)} packages): {', '.join(already)}")

    if not missing:
        ok("All packages already installed, skipping.")
        return

    info(f"Installing {len(missing)} packages: {', '.join(missing)}")
    try:
        run(f"sudo pacman -S --needed --noconfirm {' '.join(missing)}")
        ok("Packages installed successfully.")
    except subprocess.CalledProcessError:
        error("Package installation failed. Check your internet connection and package names.")
        sys.exit(1)

def clone_repo(tmpdir: str) -> str:
    header("Cloning Repository")
    dest = os.path.join(tmpdir, "bspwm-dotfiles")
    info(f"Cloning: {REPO_URL}")
    try:
        run(f"git clone --depth=1 {REPO_URL} {dest}")
        ok("Repository cloned successfully.")
    except subprocess.CalledProcessError:
        error("git clone failed. Check your internet connection.")
        sys.exit(1)
    return dest

def copy_configs(dotfiles_path: str):
    header("Copying Config Files")
    config_home = Path.home() / ".config"
    config_home.mkdir(parents=True, exist_ok=True)

    for src_name, dst_name in CONFIG_MAP.items():
        src = Path(dotfiles_path) / src_name
        dst = config_home / dst_name

        if not src.exists():
            warn(f"Source not found, skipped: {src_name}/")
            continue

        # Back up existing config
        if dst.exists():
            backup = Path(str(dst) + ".bak")
            warn(f"Backing up '{dst_name}' → {backup.name}")
            if backup.exists():
                shutil.rmtree(backup) if backup.is_dir() else backup.unlink()
            shutil.copytree(dst, backup) if dst.is_dir() else shutil.copy2(dst, backup)
            shutil.rmtree(dst) if dst.is_dir() else dst.unlink()

        shutil.copytree(src, dst)
        ok(f"~/.config/{dst_name}  ←  {src_name}/")

def fix_permissions():
    header("Setting Permissions")
    targets = [
        Path.home() / ".config/bspwm/bspwmrc",
        Path.home() / ".config/polybar/launch.sh",
    ]
    for f in targets:
        if f.exists():
            f.chmod(0o755)
            ok(f"{f.name} → +x")

def remove_nvidia_line():
    header("Removing nvidia-settings Line")
    bspwmrc = Path.home() / ".config/bspwm/bspwmrc"
    if not bspwmrc.exists():
        warn("bspwmrc not found, skipped.")
        return
    lines = bspwmrc.read_text().splitlines()
    filtered = [l for l in lines if "nvidia-settings" not in l]
    bspwmrc.write_text("\n".join(filtered) + "\n")
    ok("Removed nvidia-settings line from bspwmrc.")

def fish_shell_prompt():
    header("Fish Shell")
    fish_path = shutil.which("fish")
    if not fish_path:
        warn("fish not found, skipping.")
        return
    if "fish" in os.environ.get("SHELL", ""):
        ok("Default shell is already fish.")
        return
    print(f"  Current shell: {os.environ.get('SHELL', 'unknown')}")
    answer = input(f"  Set fish as default shell? [{BOLD}y{RESET}/n]: ").strip().lower()
    if answer in ("y", "yes", ""):
        try:
            run(f"chsh -s {fish_path}")
            ok(f"Default shell set to {fish_path}.")
            info("Log out and back in for the change to take effect.")
        except subprocess.CalledProcessError:
            warn("chsh failed. Run manually: 'chsh -s $(which fish)'")
    else:
        info("Skipped fish shell change.")

def print_summary():
    header("Installation Complete")
    ok("All packages installed.")
    ok("Config files copied to ~/.config.")
    ok("nvidia-settings line removed from bspwmrc.")
    print(f"""
  {BOLD}Next steps:{RESET}

  1. Add to ~/.xinitrc to start bspwm:
       {CYAN}exec bspwm{RESET}
     Then run: {CYAN}startx{RESET}

  2. Update monitor name (currently HDMI-0):
       {CYAN}~/.config/bspwm/bspwmrc{RESET}       → xrandr line
       {CYAN}~/.config/polybar/config.ini{RESET}   → monitor = HDMI-0

  3. Update wallpaper path:
       {CYAN}~/.config/bspwm/bspwmrc{RESET}
       → feh --bg-scale ~/Pictures/Wallpaper/1.jpg

  4. Check ALSA sink number:
       {CYAN}pactl list sinks short{RESET}
       {CYAN}~/.config/polybar/modules.ini{RESET}  → sink = 51

  5. Enable NetworkManager:
       {CYAN}sudo systemctl enable --now NetworkManager{RESET}

  6. Open neovim once to auto-install plugins:
       {CYAN}nvim{RESET}
""")

def main():
    print(f"""
{BOLD}{CYAN}
  ██████╗ ███████╗██████╗ ██╗    ██╗███╗   ███╗
  ██╔══██╗██╔════╝██╔══██╗██║    ██║████╗ ████║
  ██████╔╝███████╗██████╔╝██║ █╗ ██║██╔████╔██║
  ██╔══██╗╚════██║██╔═══╝ ██║███╗██║██║╚██╔╝██║
  ██████╔╝███████║██║     ╚███╔███╔╝██║ ╚═╝ ██║
  ╚═════╝ ╚══════╝╚═╝      ╚══╝╚══╝ ╚═╝     ╚═╝
                                    dotfiles installer
{RESET}""")

    if not is_arch():
        error("Arch Linux (pacman) is required.")
        sys.exit(1)

    install_packages()

    with tempfile.TemporaryDirectory() as tmpdir:
        dotfiles_path = clone_repo(tmpdir)
        copy_configs(dotfiles_path)

    fix_permissions()
    remove_nvidia_line()
    fish_shell_prompt()
    print_summary()

if __name__ == "__main__":
    main()
