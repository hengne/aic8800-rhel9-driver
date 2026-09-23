#!/bin/bash
#
# AIC8800 USB WiFi6 driver - one-click installer for RHEL/AlmaLinux/Rocky 9
# Downloads and installs the v1.0.0 release packages from GitHub.
#
set -e

VERSION="1.0.0"
BASE_URL="https://github.com/hengne/aic8800-rhel9-driver/releases/download/v${VERSION}"
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

if [ "$(id -u)" -ne 0 ]; then
    echo "请使用 root 运行：sudo bash $0"
    exit 1
fi

if ! command -v dnf >/dev/null 2>&1; then
    echo "本安装脚本仅支持使用 dnf 的 RHEL/CentOS/AlmaLinux/Rocky 系统。"
    exit 1
fi

KVER="$(uname -r)"
PKG=""

echo "==> 正在尝试匹配当前内核 ($KVER) 的预编译 kmod 包..."
if curl -fL --retry 2 -o "$TMPDIR/aic8800-kmod.rpm" \
    "${BASE_URL}/aic8800-kmod-${VERSION}-1.el9.x86_64.rpm" 2>/dev/null; then
    if rpm -qpR "$TMPDIR/aic8800-kmod.rpm" 2>/dev/null | \
        grep -q "kernel-uname-r = ${KVER}"; then
        PKG="$TMPDIR/aic8800-kmod.rpm"
        echo "==> 找到匹配的预编译包，安装无需编译。"
    fi
fi

if [ -z "$PKG" ]; then
    echo "==> 无匹配的预编译包，改用 DKMS 包（将自动编译）..."
    curl -fL -o "$TMPDIR/aic8800-dkms.rpm" \
        "${BASE_URL}/aic8800-dkms-${VERSION}-1.el9.noarch.rpm"
    PKG="$TMPDIR/aic8800-dkms.rpm"
fi

dnf install -y "$PKG"

echo ""
echo "安装完成。请拔下 USB 网卡等待几秒后重新插回，出现 wlan0 即成功："
echo "  ip link show wlan0"
echo "  nmcli device wifi list"
