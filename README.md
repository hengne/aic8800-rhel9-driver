# AIC8800 USB WiFi6 网卡 Linux 驱动（RHEL/Rocky/AlmaLinux 9 适配版）

适用于 **AIC8800D80 系列 USB WiFi6 无线网卡**的 Linux 内核驱动，已针对
RHEL 9 系内核（5.14 回移植内核）做了编译与 API 兼容修复，并通过 DKMS 方式安装，
内核升级后会自动重新编译。

本仓库基于开源社区驱动（shenmintao/aic8800d80 的 `legacy-mcu1` 固件分支）修改，
原始代码版权归 AICSemi / Tenda 及 RivieraWaves 所有。

## 支持的硬件

- 芯片：AIC8800D80 / AIC8800DC / AIC8800DW 系列（USB 接口）
- 典型产品：绿联 UGREEN USB WiFi6 网卡、腾达 Tenda U11 / AX913B 等
- 已实测设备 ID：
  - 出厂光盘模式：`a69c:5723`（Aic MSC，虚拟光驱）
  - 网卡工作模式：`a69c:8d80`、`a69c:8d81`
- 本仓库固件对应硬件版本：`chip_id=7, chip_mcu_id=1`（legacy MCU1）

## 测试环境

| 项目 | 版本 |
| --- | --- |
| 操作系统 | AlmaLinux 9.8 |
| 内核 | 5.14.0-687.48.1 / 687.49.1.el9_8.x86_64 |
| 编译器 | gcc 11.5 |
| 安装方式 | DKMS 3.4 |

同样适用于 RHEL 9、CentOS Stream 9、Rocky Linux 9 及其他使用 el9 内核的发行版。

## 一键安装

需要 root 权限及可用的网络（用于安装依赖）。

```bash
git clone <本仓库地址> aic8800-rhel9-driver
cd aic8800-rhel9-driver
sudo ./install.sh
```

脚本会自动完成：

1. 安装依赖：`dkms gcc make kernel-devel mokutil usb_modeswitch eject`
2. 安装各芯片固件到 `/lib/firmware/aic8800*`
3. 安装 udev 规则（`aic.rules`），实现插入网卡时**自动从光盘模式切换为网卡模式**
4. 通过 DKMS 编译并安装三个内核模块：
   - `aic8800_fdrv`：WiFi 主驱动
   - `aic_load_fw`：固件加载器
   - `aic_zlp_quirk`：特定型号蓝牙 ZLP 兼容（仅对 368b:8d81 生效）

安装完成后，**拔下网卡等待几秒再重新插回**（让设备重新枚举），出现 `wlan0`
接口即成功：

```bash
ip link show wlan0
nmcli device wifi list
```

## 连接 WiFi

使用 NetworkManager：

```bash
nmcli device wifi connect "<WiFi名称>" password "<密码>"
```

## 卸载

```bash
sudo dkms remove aic8800/1.0.0 --all
sudo rm -rf /lib/firmware/aic8800* /usr/lib/udev/rules.d/aic.rules
sudo rm -f /etc/usb_modeswitch.d/1111:1111
```

## 手动编译（不使用安装脚本）

```bash
cd drivers/aic8800
make
sudo make install
sudo cp -r ../../fw/aic8800* /lib/firmware/
sudo cp ../../aic.rules /usr/lib/udev/rules.d/
sudo modprobe aic8800_fdrv
```

## 本仓库相对上游的修改

均为针对 RHEL 9 内核（版本号为 5.14，但大量回移植了 6.x 的 cfg80211 API）的
编译兼容修复，驱动会通过内核头文件中的 `RHEL_RELEASE_CODE` 宏自动识别：

- `rwnx_defs.h`：新增 `AIC_RHEL9_BACKPORT` 检测；版本特性宏在 RHEL9 上按 5.14 生效
- `rwnx_compat.h`：cfg80211 API 版本按 6.17 处理
- `rwnx_wakelock.c`：用 `wakeup_source_register/unregister` 替代 6.0 才公开的
  `wakeup_source_create/destroy`
- `rwnx_rx.c` / `rwnx_main.c`：`from_timer` 替换为 RHEL9 提供的
  `timer_container_of`；适配 `cfg80211_rx_spurious_frame`、信道切换通知等新签名
- `rwnx_radar.c`：适配 `cfg80211_cac_event` 新参数
- `aic_priv_cmd.c` / `aic_priv_cmd.h` / `rwnx_main.h`：monitor channel 相关
  函数签名与声明同步适配

## 故障排查

**1. 插入后显示为 3.6MB 的 U 盘/光盘（Aic MSC），没有无线接口**

这是网卡出厂的驱动安装盘模式。安装本驱动后 udev 会自动 eject 切换；
若未自动切换，手动执行：

```bash
sudo eject /dev/sdX   # sdX 为网卡对应的光盘设备，可用 lsblk 查看
```

**2. 固件上传超时，日志出现 `bin upload fail: 170400`**

说明固件与硬件 MCU 版本不匹配。`dmesg` 中查看：

```bash
sudo dmesg | grep -E 'chip_id|chip_mcu'
```

`chip_mcu_id=1` 必须使用本仓库（legacy-mcu1）固件；`chip_mcu_id=0` 则需改用
上游 main 分支固件。更换固件后必须重新运行 `install.sh`。

**3. 日志出现 `40500000 rd fail`、`chip_id=0` 或 USB 枚举超时（error -110/-62/-71）**

通常是之前固件崩溃导致芯片 MCU 挂死，或 USB 口供电/接触问题：

1. 拔下网卡，静置 3~5 分钟让芯片彻底放电后再插回
2. **更换一个 USB 口**（优先机箱主板后置端口，去掉 USB 延长线/底座直插）
3. 把网卡插到其他电脑确认硬件是否正常
4. 仍无法枚举可重启主机复位 USB 控制器

**4. Secure Boot**

DKMS 模块在开启 Secure Boot 时需要签名才能加载。可在 BIOS 中关闭 Secure Boot，
或使用 `mokutil` 导入 DKMS 公钥。本驱动在 Legacy BIOS（无 Secure Boot）环境实测通过。

## 目录结构

```
aic8800-rhel9-driver/
├── install.sh            # DKMS 一键安装脚本
├── dkms.conf             # DKMS 配置
├── aic.rules             # udev 自动模式切换规则
├── usb_modeswitch/       # usb_modeswitch 配置
├── fw/                   # 各芯片型号固件
└── drivers/aic8800/      # 驱动源码
    ├── aic8800_fdrv/     # WiFi 主驱动
    ├── aic_load_fw/      # 固件加载器
    └── aic_zlp_quirk/    # 蓝牙兼容模块
```

## 许可与免责声明

- 驱动及固件源码沿用上游许可证（GPL），版权归原作者所有
- 本仓库仅用于学习与个人硬件适配，不对第三方固件做任何担保
