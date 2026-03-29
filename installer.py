#!/usr/bin/env python3
"""
bspwm_dotfiles installer
Paketleri yükler ve config dosyalarını ~/.config altına kopyalar.
Kaynak: https://github.com/lionesslie/bspwm_dotfiles
"""

import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path

# ── Renkler ──────────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def info(msg):    print(f"{CYAN}[*]{RESET} {msg}")
def ok(msg):      print(f"{GREEN}[✓]{RESET} {msg}")
def warn(msg):    print(f"{YELLOW}[!]{RESET} {msg}")
def error(msg):   print(f"{RED}[✗]{RESET} {msg}")
def header(msg):  print(f"\n{BOLD}{CYAN}{'─'*50}{RESET}\n{BOLD}  {msg}{RESET}\n{BOLD}{CYAN}{'─'*50}{RESET}")

# ── Paket listesi ─────────────────────────────────────────────────────────────
PACMAN_PACKAGES = [
    "bspwm",
    "sxhkd",
    "polybar",
    "picom",
    "dunst",
    "kitty",
    "rofi",
    "thunar",
    "feh",
    "fish",
    "udiskie",
    "udisks2",
    "ttf-jetbrains-mono-nerd",
    "ttf-material-design-icons-extended",
    "papirus-icon-theme",
    "playerctl",
    "brightnessctl",
    "alsa-utils",
    "xorg-xrandr",
    "xorg-xinput",
    "xdg-user-dirs",
    "flameshot",
]

# ── Repo ──────────────────────────────────────────────────────────────────────
REPO_URL        = "https://github.com/lionesslie/bspwm_dotfiles"
DOTFILES_SUBDIR = "bspwm-dotfiles"

CONFIG_MAP = {
    "bspwm":   "bspwm",
    "sxhkd":   "sxhkd",
    "polybar":  "polybar",
    "picom":    "picom",
    "dunst":    "dunst",
    "kitty":    "kitty",
    "rofi":     "rofi",
    "fish":     "fish",
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
    header("Paketler Yükleniyor")

    if not is_arch():
        error("Bu installer sadece Arch Linux (pacman) destekler.")
        sys.exit(1)

    already, missing = [], []
    for pkg in PACMAN_PACKAGES:
        result = run(f"pacman -Qi {pkg}", check=False, capture=True)
        if result.returncode == 0:
            already.append(pkg)
        else:
            missing.append(pkg)

    if already:
        ok(f"Zaten yüklü ({len(already)} paket): {', '.join(already)}")

    if not missing:
        ok("Tüm paketler zaten yüklü, atlanıyor.")
        return

    info(f"Yüklenecek {len(missing)} paket: {', '.join(missing)}")
    try:
        run(f"sudo pacman -S --needed --noconfirm {' '.join(missing)}")
        ok("Paketler başarıyla yüklendi.")
    except subprocess.CalledProcessError:
        error("Paket kurulumu başarısız. İnternet bağlantını ve paket adlarını kontrol et.")
        sys.exit(1)

def clone_repo(tmpdir: str) -> str:
    header("Repo İndiriliyor")
    dest = os.path.join(tmpdir, "bspwm_dotfiles")
    info(f"Klonlanıyor: {REPO_URL}")
    try:
        run(f"git clone --depth=1 {REPO_URL} {dest}")
        ok("Repo başarıyla indirildi.")
    except subprocess.CalledProcessError:
        error("git clone başarısız. İnternet bağlantını kontrol et.")
        sys.exit(1)
    return os.path.join(dest, DOTFILES_SUBDIR)

def copy_configs(dotfiles_path: str):
    header("Config Dosyaları Kopyalanıyor")
    config_home = Path.home() / ".config"
    config_home.mkdir(parents=True, exist_ok=True)

    for src_name, dst_name in CONFIG_MAP.items():
        src = Path(dotfiles_path) / src_name
        dst = config_home / dst_name

        if not src.exists():
            warn(f"Kaynak bulunamadı, atlandı: {src}")
            continue

        if dst.exists():
            backup = Path(str(dst) + ".bak")
            warn(f"Mevcut '{dst_name}' yedekleniyor → {backup}")
            if backup.exists():
                shutil.rmtree(backup) if backup.is_dir() else backup.unlink()
            shutil.copytree(dst, backup) if dst.is_dir() else shutil.copy2(dst, backup)
            shutil.rmtree(dst) if dst.is_dir() else dst.unlink()

        shutil.copytree(src, dst)
        ok(f"~/.config/{dst_name}  ←  {src_name}/")

def fix_permissions():
    """bspwmrc çalıştırılabilir olmalı."""
    header("İzinler Ayarlanıyor")
    bspwmrc = Path.home() / ".config/bspwm/bspwmrc"
    if bspwmrc.exists():
        bspwmrc.chmod(0o755)
        ok("bspwmrc +x yapıldı.")
    launch_sh = Path.home() / ".config/polybar/launch.sh"
    if launch_sh.exists():
        launch_sh.chmod(0o755)
        ok("polybar/launch.sh +x yapıldı.")

def fish_shell_prompt():
    header("Fish Shell")
    fish_path = shutil.which("fish")
    if not fish_path:
        warn("fish bulunamadı, atlanıyor.")
        return
    current_shell = os.environ.get("SHELL", "")
    if "fish" in current_shell:
        ok("Varsayılan shell zaten fish.")
        return
    print(f"  Mevcut shell: {current_shell}")
    answer = input(f"  Fish'i varsayılan shell yapmak ister misin? [{BOLD}e{RESET}/h]: ").strip().lower()
    if answer in ("e", "evet", "y", "yes", ""):
        try:
            run(f"chsh -s {fish_path}")
            ok(f"Varsayılan shell {fish_path} olarak ayarlandı.")
            info("Değişikliğin etkili olması için tekrar giriş yapman gerekir.")
        except subprocess.CalledProcessError:
            warn("chsh başarısız. Manuel: 'chsh -s $(which fish)'")
    else:
        info("Fish shell değişikliği atlandı.")

def print_summary():
    header("Kurulum Tamamlandı")
    ok("Tüm paketler yüklendi.")
    ok("Config dosyaları ~/.config altına kopyalandı.")
    print(f"""
  {BOLD}Sonraki adımlar:{RESET}

  1. bspwm'i başlatmak için .xinitrc dosyana ekle:
       {CYAN}exec bspwm{RESET}
     Ardından: {CYAN}startx{RESET}

  2. Monitor adını güncelle (şu an HDMI-0):
       {CYAN}~/.config/bspwm/bspwmrc{RESET}   → xrandr satırı
       {CYAN}~/.config/polybar/config.ini{RESET} → monitor = HDMI-0

  3. Duvar kağıdı yolunu güncelle:
       {CYAN}~/.config/bspwm/bspwmrc{RESET}
       → feh --bg-scale ~/Resimler/Wallpaper/1.jpg

  4. ALSA sink numarasını kontrol et:
       {CYAN}~/.config/polybar/modules.ini{RESET} → sink = 51
       Kendi sink numarası için: {CYAN}pactl list sinks short{RESET}

  5. NVIDIA kullanıyorsan:
       {CYAN}nvidia-settings --load-config-only{RESET}
     satırı bspwmrc'de zaten mevcut.
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
        error("Arch Linux (pacman) gereklidir.")
        sys.exit(1)

    install_packages()

    with tempfile.TemporaryDirectory() as tmpdir:
        dotfiles_path = clone_repo(tmpdir)
        copy_configs(dotfiles_path)

    fix_permissions()
    fish_shell_prompt()
    print_summary()

if __name__ == "__main__":
    main()
