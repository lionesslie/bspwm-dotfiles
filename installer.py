#!/usr/bin/env python3

import os
import shutil
import sys
import subprocess
from pathlib import Path

# Renkler
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

PACKAGES = [
    # WM & temel araçlar
    "bspwm",
    "dunst",
    "fish",
    "kitty",
    "picom",
    "polybar",
    "rofi",
    "sxhkd",
    # Ekstra araçlar
    "feh",
    "xorg-xinput",
    "xorg-xrandr",
    "udisks2",
    "firefox",
]

# Nvidia sürücü seçenekleri
NVIDIA_DRIVERS = {
    "1": {
        "label": "nvidia-dkms (zen-kernel) — Önerilen",
        "packages": ["nvidia-dkms", "linux-zen-headers", "nvidia-utils", "nvidia-settings"],
    },
    "2": {
        "label": "nvidia (standart kernel)",
        "packages": ["nvidia", "nvidia-utils", "nvidia-settings"],
    },
    "3": {
        "label": "nvidia-open-dkms (açık kaynak, RTX 2000+)",
        "packages": ["nvidia-open-dkms", "linux-zen-headers", "nvidia-utils", "nvidia-settings"],
    },
    "4": {
        "label": "nvidia-390xx (eski kartlar, AUR)",
        "packages": ["nvidia-390xx-dkms", "nvidia-390xx-utils", "nvidia-390xx-settings"],
    },
    "5": {
        "label": "Atla — Nvidia driver kurma",
        "packages": [],
    },
}

DOTFILES = [
    "bspwm",
    "dunst",
    "fish",
    "kitty",
    "picom",
    "polybar",
    "rofi",
    "sxhkd",
]

def print_banner():
    print(f"""
{CYAN}{BOLD}╔══════════════════════════════════════╗
║      bspwm Dotfiles Installer        ║
╚══════════════════════════════════════╝{RESET}
""")

def log_ok(msg):
    print(f"  {GREEN}✔{RESET}  {msg}")

def log_skip(msg):
    print(f"  {YELLOW}⚠{RESET}  {msg}")

def log_err(msg):
    print(f"  {RED}✘{RESET}  {msg}")

def log_info(msg):
    print(f"  {CYAN}→{RESET}  {msg}")

def is_installed(pkg: str) -> bool:
    """Paketin sistemde kurulu olup olmadığını kontrol et."""
    result = subprocess.run(
        ["pacman", "-Qi", pkg],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return result.returncode == 0

def select_nvidia_driver() -> list:
    """Kullanıcıya nvidia sürücüsünü seçtir."""
    print(f"\n{BOLD}[Nvidia Sürücü Seçimi]{RESET}")
    print()

    for key, val in NVIDIA_DRIVERS.items():
        print(f"  {CYAN}{key}{RESET}) {val['label']}")

    print()
    while True:
        ans = input(f"  {YELLOW}Seçiminiz (1-5) [{BOLD}1{RESET}{YELLOW}]: {RESET}").strip()
        if ans == "":
            ans = "1"
        if ans in NVIDIA_DRIVERS:
            chosen = NVIDIA_DRIVERS[ans]
            if chosen["packages"]:
                log_info(f"Seçildi: {chosen['label']}")
            else:
                log_skip("Nvidia kurulumu atlandı.")
            return chosen["packages"]
        log_err("Geçersiz seçim, tekrar deneyin.")


def install_packages():
    """Eksik paketleri sudo pacman ile kur."""
    print(f"\n{BOLD}[Paket Kurulumu]{RESET}")

    # Nvidia seçimi
    nvidia_pkgs = select_nvidia_driver()

    all_packages = PACKAGES + nvidia_pkgs
    missing = [p for p in all_packages if not is_installed(p)]

    print()
    if not missing:
        log_ok("Tüm paketler zaten kurulu, atlanıyor.")
        return True

    log_info(f"Kurulacak paketler: {', '.join(missing)}")
    print()

    ans = input(f"  {YELLOW}Bu paketler kurulsun mu? (e/h) [{BOLD}e{RESET}{YELLOW}]: {RESET}").strip().lower()
    if ans == "h":
        log_skip("Paket kurulumu atlandı.")
        return True

    print()
    log_info("sudo pacman -S çalıştırılıyor...\n")

    result = subprocess.run(
        ["sudo", "pacman", "-S", "--needed", "--noconfirm"] + missing
    )

    if result.returncode == 0:
        log_ok("Tüm paketler başarıyla kuruldu.")
        return True
    else:
        log_err("Paket kurulumu sırasında hata oluştu.")
        return False


def backup_existing(target: Path):
    """Mevcut klasörü .bak olarak yedekle."""
    backup = Path(str(target) + ".bak")
    if backup.exists():
        shutil.rmtree(backup)
    shutil.copytree(target, backup) if target.is_dir() else shutil.copy2(target, backup)
    log_skip(f"Yedeklendi: {target} → {backup}")

def install(dotfiles_dir: Path, config_dir: Path, backup: bool):
    success, skipped, failed = 0, 0, 0

    for name in DOTFILES:
        src = dotfiles_dir / name
        dst = config_dir / name

        if not src.exists():
            log_err(f"{name}: kaynak bulunamadı, atlandı.")
            failed += 1
            continue

        print(f"\n{BOLD}[{name}]{RESET}")

        # Yedek al
        if dst.exists() and backup:
            backup_existing(dst)

        # Kopyala
        try:
            if dst.exists():
                shutil.rmtree(dst) if dst.is_dir() else dst.unlink()

            shutil.copytree(src, dst) if src.is_dir() else shutil.copy2(src, dst)
            log_ok(f"Kopyalandı → {dst}")

            # bspwmrc ve launch.sh için çalıştırma izni
            for exe_file in dst.rglob("*"):
                if exe_file.is_file() and exe_file.suffix in ("", ".sh"):
                    exe_file.chmod(exe_file.stat().st_mode | 0o111)

            success += 1
        except Exception as e:
            log_err(f"{name}: hata — {e}")
            failed += 1

    return success, skipped, failed


def main():
    print_banner()

    # Dotfiles konumu: script ile aynı dizindeki bspwm-dotfiles/ klasörü
    # git clone https://github.com/lionesslie/bspwm_dotfiles → bspwm_dotfiles/
    # ├── install.py
    # └── bspwm-dotfiles/
    script_dir   = Path(__file__).parent.resolve()
    dotfiles_dir = script_dir / "bspwm-dotfiles"

    if not dotfiles_dir.exists():
        log_err("'bspwm-dotfiles' klasörü bulunamadı.")
        log_info("Kullanım: git clone https://github.com/lionesslie/bspwm_dotfiles")
        log_info("          cd bspwm_dotfiles && python3 install.py")
        sys.exit(1)

    config_dir = Path.home() / ".config"
    config_dir.mkdir(parents=True, exist_ok=True)

    # 1) Paket kurulumu
    install_packages()

    # 2) Dotfile kopyalama
    print(f"\n{BOLD}[Dotfile Kopyalama]{RESET}")
    log_info(f"Kaynak : {dotfiles_dir}")
    log_info(f"Hedef  : {config_dir}")

    # Yedekleme sorusu
    print()
    ans = input(f"  {YELLOW}Mevcut config'leri yedeklemek ister misiniz? (e/h) [{BOLD}e{RESET}{YELLOW}]: {RESET}").strip().lower()
    do_backup = ans != "h"

    print()
    success, skipped, failed = install(dotfiles_dir, config_dir, backup=do_backup)

    print(f"""
{BOLD}══════════════════════════════════════{RESET}
  {GREEN}✔ Başarılı : {success}{RESET}
  {YELLOW}⚠ Atlanan  : {skipped}{RESET}
  {RED}✘ Hatalı   : {failed}{RESET}
{BOLD}══════════════════════════════════════{RESET}
""")

    if success > 0:
        print(f"  {CYAN}Kurulum tamamlandı! bspwm'i yeniden başlatın.{RESET}\n")


if __name__ == "__main__":
    main()
