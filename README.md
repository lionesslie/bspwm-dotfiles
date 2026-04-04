<div align="center">

# 🌿 bspwm-dotfiles

**bspwm** tabanlı minimal ve modern bir Arch Linux masaüstü kurulumu.

![bspwm](https://img.shields.io/badge/WM-bspwm-blue?style=for-the-badge&logo=linux)
![Arch](https://img.shields.io/badge/OS-Arch_Linux-1793D1?style=for-the-badge&logo=arch-linux)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

</div>

---

## 📦 İçerik

| Klasör | Araç | Açıklama |
|--------|------|----------|
| `bspwm/` | [bspwm](https://github.com/baskerville/bspwm) | Pencere yöneticisi |
| `sxhkd/` | [sxhkd](https://github.com/baskerville/sxhkd) | Kısayol yöneticisi |
| `polybar/` | [Polybar](https://github.com/polybar/polybar) | Status bar |
| `picom/` | [Picom](https://github.com/yshui/picom) | Compositor |
| `dunst/` | [Dunst](https://dunst-project.org) | Bildirim yöneticisi |
| `kitty/` | [Kitty](https://sw.kovidgoyal.net/kitty/) | Terminal |
| `rofi/` | [Rofi](https://github.com/davatorium/rofi) | Uygulama başlatıcı |
| `fish/` | [Fish](https://fishshell.com) | Shell |

---

## ✨ Özellikler

- 7 workspace, renkli ikonlarla polybar
- Gölge ve fade efektleri ile **picom** compositor
- **Catppuccin** temalı rofi ve **Cosmic** temalı kitty
- Türkçe klavye + Rusça desteği (`Alt+Shift` ile geçiş)
- Saat, sıcaklık, CPU, RAM, ses, ağ ve batarya modülleriyle tam polybar
- `feh` ile duvar kağıdı desteği
- `udiskie` ile otomatik disk bağlama
- `JetBrainsMono Nerd Font` + `Material Design Icons` ile ikonlu arayüz

---

## 🚀 Kurulum

### Gereksinimler

- Arch Linux
- `git` ve `python`

### Tek Komutla Kur

```bash
git clone https://github.com/lionesslie/bspwm_dotfiles
cd bspwm_dotfiles
python installer.py
```

`installer.py` otomatik olarak şunları yapar:

1. Gerekli tüm paketleri `pacman` ile yükler
2. Mevcut configlerini `.bak` uzantısıyla yedekler
3. Config dosyalarını `~/.config/` altına kopyalar
4. `bspwmrc` ve `launch.sh` dosyalarına çalıştırma izni verir (`+x`)
5. Fish'i varsayılan shell yapıp yapmamayı sorar

---

## 📋 Yüklenen Paketler

```
bspwm  sxhkd  polybar  picom  dunst  kitty  rofi
thunar  feh  fish  udiskie  udisks2
ttf-jetbrains-mono-nerd  ttf-material-design-icons-extended
papirus-icon-theme  playerctl  brightnessctl
alsa-utils  xorg-xrandr  xorg-xinput  flameshot
```

---

## ⚙️ Kurulum Sonrası

### bspwm'i başlatma
```bash
# ~/.xinitrc dosyasına ekle:
exec bspwm

# Ardından:
startx
```

### Monitor ayarı
`~/.config/bspwm/bspwmrc` ve `~/.config/polybar/config.ini` dosyalarında monitor adını güncelle:
```bash
# Mevcut monitörleri görmek için:
xrandr --listmonitors

# bspwmrc'de:
xrandr --output HDMI-0 --mode 1920x1080 --rate 180 &

# polybar/config.ini'de:
monitor = HDMI-0
```

### Duvar kağıdı
```bash
# ~/.config/bspwm/bspwmrc
feh --bg-scale ~/Resimler/Wallpaper/1.jpg &
```

### ALSA ses ayarı
Polybar `modules.ini` dosyasında sink numarasını kontrol et:
```bash
# Kendi sink numaranı öğrenmek için:
pactl list sinks short

# modules.ini'de:
sink = 51   ← burası değişebilir
```

### Klavye düzeni
Varsayılan olarak **Türkçe Q** ve **Rusça** yüklü gelir. Değiştirmek için `~/.config/sxhkd/sxhkdrc` ile masaüstü ayarlarından düzenleyebilirsin.

---

## ⌨️ Kısayollar

| Kısayol | Eylem |
|---------|-------|
| `Super + Enter` | Terminal (kitty) |
| `Super + D` | Uygulama başlatıcı (rofi) |
| `Super + E` | Dosya yöneticisi (thunar) |
| `Super + C` | Pencereyi kapat |
| `Super + M` | Monocle layout geçişi |
| `Super + T` | Tiled moda al |
| `Super + S` | Floating moda al |
| `Super + F` | Fullscreen |
| `Super + Alt + Q` | bspwm'den çık |
| `Super + Alt + R` | bspwm'i yeniden başlat |
| `Super + 1-9` | Workspace değiştir |
| `Super + Shift + 1-9` | Pencereyi workspace'e taşı |
| `Super + H/J/K/L` | Odak değiştir (vim yönleri) |
| `Super + Shift + H/J/K/L` | Pencereyi taşı |
| `Super + Alt + H/J/K/L` | Pencereyi genişlet |

---

## 📁 Dosya Yapısı

```
bspwm_dotfiles/
├── bspwm-dotfiles/
│   ├── bspwm/
│   │   └── bspwmrc
│   ├── sxhkd/
│   │   └── sxhkdrc
│   ├── polybar/
│   │   ├── config.ini
│   │   ├── colors.ini
│   │   ├── modules.ini
│   │   └── launch.sh
│   ├── picom/
│   │   └── picom.conf
│   ├── dunst/
│   │   └── dunstrc
│   ├── kitty/
│   │   └── kitty.conf
│   ├── rofi/
│   │   ├── config.rasi
│   │   └── catppuccin.rasi
│   └── fish/
│       ├── config.fish
│       └── fish_variables
└── installer.py
```
