%global debug_package %{nil}
%{!?kver:%global kver %(uname -r)}
%global kmoddir kernel/drivers/net/wireless/aic8800

Name:           aic8800-kmod
Version:        1.0.0
Release:        1%{?dist}
Summary:        Prebuilt AIC8800 USB WiFi6 kernel modules for RHEL 9

License:        GPL-2.0-only
URL:            https://github.com/hengne/aic8800-rhel9-driver
Source0:        aic8800-rhel9-driver-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  kernel-devel-uname-r = %{kver}

Requires:       kernel-uname-r = %{kver}
Requires:       usb_modeswitch
Requires:       util-linux
Requires:       kmod
Conflicts:      aic8800-dkms

%description
Prebuilt kernel modules (aic8800_fdrv, aic_load_fw, aic_zlp_quirk) for
AIC8800D80 based USB WiFi6 adapters, built for kernel %{kver} on RHEL/AlmaLinux/
Rocky/CentOS 9. Includes the legacy MCU1 firmware and udev rules that switch the
adapter automatically from its factory CD mode to WiFi mode.

For automatic rebuilds across kernel updates install aic8800-dkms instead.

%prep
%autosetup -n aic8800-rhel9-driver-%{version}

%build
make -C drivers/aic8800 KVER=%{kver} KDIR=/usr/src/kernels/%{kver}

%install
rm -rf %{buildroot}

install -Dpm0644 drivers/aic8800/aic8800_fdrv/aic8800_fdrv.ko \
  %{buildroot}/usr/lib/modules/%{kver}/%{kmoddir}/aic8800_fdrv.ko
install -Dpm0644 drivers/aic8800/aic_load_fw/aic_load_fw.ko \
  %{buildroot}/usr/lib/modules/%{kver}/%{kmoddir}/aic_load_fw.ko
install -Dpm0644 drivers/aic8800/aic_zlp_quirk/aic_zlp_quirk.ko \
  %{buildroot}/usr/lib/modules/%{kver}/%{kmoddir}/aic_zlp_quirk.ko

install -Dpm0644 aic.rules \
  %{buildroot}/usr/lib/udev/rules.d/aic.rules
install -Dpm0644 usb_modeswitch/1111_1111 \
  %{buildroot}/etc/usb_modeswitch.d/1111:1111

install -d -m 0755 %{buildroot}/usr/lib/firmware
cp -a fw/aic8800* %{buildroot}/usr/lib/firmware/

%post
/usr/sbin/depmod -a %{kver} || :

%postun
/usr/sbin/depmod -a %{kver} || :

%files
%dir /usr/lib/modules/%{kver}/%{kmoddir}
/usr/lib/modules/%{kver}/%{kmoddir}/aic8800_fdrv.ko
/usr/lib/modules/%{kver}/%{kmoddir}/aic_load_fw.ko
/usr/lib/modules/%{kver}/%{kmoddir}/aic_zlp_quirk.ko
/usr/lib/udev/rules.d/aic.rules
%config(noreplace) /etc/usb_modeswitch.d/1111:1111
/usr/lib/firmware/aic8800*

%changelog
* Wed Sep 23 2026 hengne <hengne@users.noreply.github.com> - 1.0.0-1
- First release: prebuilt AIC8800D80 modules for RHEL/AlmaLinux/Rocky 9.
- Legacy MCU1 firmware and automatic udev mode switching.
