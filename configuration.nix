{ config, pkgs, ... }:
{
  imports = [ ./hardware-configuration.nix ];

  # ── Bootloader ────────────────────────────────────────────────────────────
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;
  boot.kernelPackages = pkgs.linuxPackages_latest;

  # ── Ağ ───────────────────────────────────────────────────────────────────
  networking.hostName = "montana";
  networking.networkmanager.enable = true;

  # ── Saat / Dil ───────────────────────────────────────────────────────────
  time.timeZone = "Europe/Istanbul";
  i18n.defaultLocale = "tr_TR.UTF-8";
  i18n.extraLocaleSettings = {
    LC_ADDRESS        = "tr_TR.UTF-8";
    LC_IDENTIFICATION = "tr_TR.UTF-8";
    LC_MEASUREMENT    = "tr_TR.UTF-8";
    LC_MONETARY       = "tr_TR.UTF-8";
    LC_NAME           = "tr_TR.UTF-8";
    LC_NUMERIC        = "tr_TR.UTF-8";
    LC_PAPER          = "tr_TR.UTF-8";
    LC_TELEPHONE      = "tr_TR.UTF-8";
    LC_TIME           = "tr_TR.UTF-8";
  };

  # ── Klavye ───────────────────────────────────────────────────────────────
  services.xserver.xkb = { layout = "tr"; variant = ""; };
  console.keyMap = "trq";

  # ── Xorg / Display / WM ──────────────────────────────────────────────────
  services.xserver = {
    enable = true;
    videoDrivers = [ "nvidia" ];
    displayManager.lightdm = {
      enable = true;
      greeters.gtk.enable = true;
    };
    windowManager.bspwm.enable = true;
  };

  # ── NVIDIA ───────────────────────────────────────────────────────────────
  hardware.graphics = {
    enable = true;
    enable32Bit = true;
  };

  hardware.nvidia = {
    modesetting.enable = true;
    powerManagement.enable = false;
    powerManagement.finegrained = false;
    open = false;
    nvidiaSettings = true;
    package = config.boot.kernelPackages.nvidiaPackages.stable;
  };

  # ── Ortam Değişkenleri ───────────────────────────────────────────────────
  environment.sessionVariables = {
    LIBVA_DRIVER_NAME          = "nvidia";
    __GLX_VENDOR_LIBRARY_NAME  = "nvidia";
    GBM_BACKEND                = "nvidia-drm";
    # Ryujinx / Ryubing için Vulkan ICD
    VK_ICD_FILENAMES           = "/run/opengl-driver/share/vulkan/icd.d/nvidia_icd.x86_64.json";
  };

  # ── Ses (PipeWire) ───────────────────────────────────────────────────────
  hardware.pulseaudio.enable = false;
  security.rtkit.enable = true;
  services.pipewire = {
    enable = true;
    alsa.enable = true;
    alsa.support32Bit = true;
    pulse.enable = true;
  };

  # ── Steam / Oyun ─────────────────────────────────────────────────────────
  programs.steam = {
    enable = true;
    remotePlay.openFirewall = true;
    gamescopeSession.enable = true;
    extraCompatPackages = with pkgs; [ proton-ge-bin ];
  };
  programs.gamemode.enable = true;

  # ── Flatpak (Ryubing için) ────────────────────────────────────────────────
  services.flatpak.enable = true;

  # ── XDG Portal (Flatpak GUI uygulamaları için zorunlu) ───────────────────
  xdg.portal = {
    enable = true;
    extraPortals = [ pkgs.xdg-desktop-portal-gtk ];
    # bspwm'de config portal seçimi için
    config.common.default = "gtk";
  };

  # ── Disk Yönetimi / Polkit ───────────────────────────────────────────────
  services.udisks2.enable = true;

  security.polkit = {
    enable = true;
    extraConfig = ''
      polkit.addRule(function(action, subject) {
        if ((action.id == "org.freedesktop.udisks2.filesystem-mount" ||
             action.id == "org.freedesktop.udisks2.filesystem-mount-system") &&
            subject.isInGroup("wheel")) {
          return polkit.Result.YES;
        }
      });
    '';
  };

  # ── Shell ────────────────────────────────────────────────────────────────
  programs.fish.enable = true;

  # ── Kullanıcı ────────────────────────────────────────────────────────────
  users.users."honey" = {
    isNormalUser = true;
    description  = "honey";
    extraGroups  = [ "networkmanager" "wheel" "video" "audio" ];
    shell        = pkgs.fish;
    packages     = with pkgs; [];
  };

  # ── Paketler ─────────────────────────────────────────────────────────────
  nixpkgs.config.allowUnfree = true;

  environment.systemPackages = with pkgs; [
    bspwm sxhkd picom feh dunst rofi polybar
    kitty alacritty git neovim fastfetch
    udiskie thunar
    brave vscode flameshot
    papirus-icon-theme materia-theme
    xinput playerctl spotify
    mangohud heroic protonup-qt eden prismlauncher
    flatpak wget wine-staging flightgear
    unzip
    nftables
  ];

  # ── Fontlar ──────────────────────────────────────────────────────────────
  fonts.packages = with pkgs; [
    nerd-fonts.jetbrains-mono
    nerd-fonts.symbols-only
    material-design-icons
    unifont
  ];

  systemd.services.zapret = {
    description = "DPI bypass service";
    after = [ "network.target" ];
    wantedBy = [ "multi-user.target" ];
    serviceConfig = {
      ExecStart = "/nix/store/nds7al2dh9z4110hipw92ya7wpbrx2ac-zapret-72.12/bin/nfqws --pidfile=/run/nfqws.pid --wsize=1500 --dpi-desync=disorder --dpi-desync-ttl=0 --qnum=200";
      PIDFile = "/run/nfqws.pid";
      Restart = "always";
      Type = "simple";
    };
  };

  system.stateVersion = "26.05";
}
