#!/usr/bin/env bash

# Rofi powermenu script
# JetBrainsMono Nerd Font + Material Design Icons kullanan setup için

SHUTDOWN="󰐥 Kapat"
REBOOT="󰑐 Yeniden Başlat"
LOGOUT="󰍃 Çıkış Yap"
LOCK="󰌾 Ekranı Kilitle"
CANCEL="󰅖 İptal"

CHOSEN=$(echo -e "$SHUTDOWN\n$REBOOT\n$LOGOUT\n$LOCK\n$CANCEL" \
    | rofi -dmenu \
        -p "Güç Menüsü" \
        -theme-str 'window {width: 280px;}' \
        -theme-str 'listview {lines: 5;}' \
        -no-custom \
        -i)

case "$CHOSEN" in
    "$SHUTDOWN")
        systemctl poweroff ;;
    "$REBOOT")
        systemctl reboot ;;
    "$LOGOUT")
        bspc quit ;;
    "$LOCK")
        # i3lock, betterlockscreen, slock - hangisi kuruluysa
        if command -v betterlockscreen &>/dev/null; then
            betterlockscreen -l
        elif command -v i3lock &>/dev/null; then
            i3lock
        else
            slock
        fi ;;
    *)
        exit 0 ;;
esac
