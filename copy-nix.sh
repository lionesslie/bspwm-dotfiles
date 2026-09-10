#!/bin/sh

# 1. Kullanıcı konfigürasyonlarını kopyala (~/.config)
echo "📂 Kullanıcı ayarları ~/.config klasörüne kopyalanıyor..."
mkdir -p ~/.config

# Belirttiğin tüm klasörleri kopyalar
cp -r bspwm sxhkd dunst fish gtk-3.0 kitty nvim picom polybar rofi ~/.config/

# bspwmrc için çalıştırma izni ver (Açılışta siyah ekranda kalmamak için şart)
if [ -f ~/.config/bspwm/bspwmrc ]; then
    chmod +x ~/.config/bspwm/bspwmrc
    echo "✅ bspwmrc dosyasına çalıştırma izni verildi."
fi

# 2. Sistem konfigürasyonunu kopyala (/etc/nixos)
if [ -f "configuration.nix" ]; then
    echo "⚙️ Sistem ayarları /etc/nixos/ konumuna kopyalanıyor..."
    
    # Eğer orada halihazırda bir dosya varsa yedekle
    if [ -f "/etc/nixos/configuration.nix" ]; then
        echo "📦 Mevcut configuration.nix dosyası configuration.nix.bak olarak yedekleniyor..."
        sudo cp /etc/nixos/configuration.nix /etc/nixos/configuration.nix.bak
    fi
    
    # Yeni dosyayı kopyala
    sudo cp configuration.nix /etc/nixos/
    echo "✅ configuration.nix başarıyla kopyalandı."
else
    echo "⚠️ Uyarı: Bulunduğunuz klasörde 'configuration.nix' dosyası bulunamadı!"
fi

echo "🎉 İşlem tamamlandı!"
