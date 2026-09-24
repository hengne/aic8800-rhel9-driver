# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright (c) 2026 Hengne Li <lihengne@hotmail.com>
# Commercial use requires a license; see COMMERCIAL-LICENSE.md
%global debug_package %{nil}
%global srcname aic8800
%global srcversion 1.0.0

Name:           aic8800-dkms
Version:        1.0.0
Release:        1%{?dist}
Summary:        DKMS AIC8800 USB WiFi6 driver for RHEL 9

License:        GPL-2.0-only
URL:            https://github.com/hengne/aic8800-rhel9-driver
Source0:        aic8800-rhel9-driver-%{version}.tar.gz

BuildArch:      noarch

Requires:       dkms
Requires:       gcc
Requires:       make
Requires:       usb_modeswitch
Requires:       util-linux
Requires:       kmod
Recommends:     kernel-devel
Conflicts:      aic8800-kmod

%description
DKMS package for AIC8800D80 based USB WiFi6 adapters on RHEL/AlmaLinux/Rocky/
CentOS 9. The modules (aic8800_fdrv, aic_load_fw, aic_zlp_quirk) are compiled
automatically on install and rebuilt on every kernel update. Includes the
legacy MCU1 firmware and udev rules that switch the adapter automatically from
its factory CD mode to WiFi mode.

%prep
%autosetup -n aic8800-rhel9-driver-%{version}

%install
rm -rf %{buildroot}

install -d -m 0755 %{buildroot}/usr/src/%{srcname}-%{srcversion}
cp -a drivers dkms.conf %{buildroot}/usr/src/%{srcname}-%{srcversion}/

install -Dpm0644 aic.rules \
  %{buildroot}/usr/lib/udev/rules.d/aic.rules
install -Dpm0644 usb_modeswitch/1111_1111 \
  %{buildroot}/etc/usb_modeswitch.d/1111:1111

install -d -m 0755 %{buildroot}/usr/lib/firmware
cp -a fw/aic8800* %{buildroot}/usr/lib/firmware/

%post
/usr/sbin/dkms add -m %{srcname} -v %{srcversion} --rpm_safe_upgrade || :
/usr/sbin/dkms build -m %{srcname} -v %{srcversion} --rpm_safe_upgrade || :
/usr/sbin/dkms install -m %{srcname} -v %{srcversion} --rpm_safe_upgrade || :

%preun
if [ $1 -eq 0 ]; then
  /usr/sbin/dkms remove -m %{srcname} -v %{srcversion} --all || :
fi

%files
/usr/src/%{srcname}-%{srcversion}
/usr/lib/udev/rules.d/aic.rules
%config(noreplace) /etc/usb_modeswitch.d/1111:1111
/usr/lib/firmware/aic8800*

%changelog
* Wed Sep 23 2026 hengne <hengne@users.noreply.github.com> - 1.0.0-1
- First release: DKMS AIC8800D80 driver for RHEL/AlmaLinux/Rocky 9.
- Auto-rebuild on kernel updates; legacy MCU1 firmware.
