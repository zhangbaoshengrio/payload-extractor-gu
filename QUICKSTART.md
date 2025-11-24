# 小白使用指南 🚀

如果你是第一次使用这个工具，按照这个指南一步一步来就可以了！

## 第一步：安装必要的软件

### 1. 确认已安装 Python

打开**终端**（Terminal），输入：

```bash
python3 --version
```

如果显示类似 `Python 3.x.x`，说明已经安装了。

**如果没有安装 Python**，使用 Homebrew 安装：

```bash
# 先安装 Homebrew（如果还没装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 然后安装 Python
brew install python3
```

### 2. 安装 payload-dumper-go

这是核心工具，必须安装：

```bash
brew install payload-dumper-go
```

安装完成后验证：

```bash
payload-dumper-go --version
```

如果显示版本号，就说明安装成功了！

## 第二步：下载本项目

### 方法一：使用 git（推荐）

在终端中输入：

```bash
# 进入你想保存项目的文件夹，比如下载文件夹
cd ~/Downloads

# 克隆项目（把下面的网址换成你的 GitHub 项目地址）
git clone https://github.com/YOUR_USERNAME/payload-extractor-gui.git

# 进入项目文件夹
cd payload-extractor-gui
```

### 方法二：直接下载 ZIP

1. 在 GitHub 项目页面点击绿色的 **Code** 按钮
2. 选择 **Download ZIP**
3. 下载后解压到某个文件夹
4. 在终端中进入这个文件夹：
   ```bash
   cd ~/Downloads/payload-extractor-gui-main
   ```

## 第三步：运行程序

在终端中，确保你在项目文件夹里，然后运行：

```bash
python3 payload_extractor_gui.py
```

就会弹出图形界面了！🎉

## 第四步：使用工具提取分区

### 1. 准备 payload.bin 文件

通常从以下地方获取：
- 手机官方 ROM 包（.zip 文件）里解压出来
- OTA 更新包里
- 第三方 ROM 网站下载的完整包

### 2. 开始提取

在弹出的界面中：

1. **选择 Payload 文件**：
   - 点击第一个"浏览..."按钮
   - 找到你的 `payload.bin` 文件并选择

2. **选择输出目录**：
   - 点击第二个"浏览..."按钮
   - 选择一个文件夹用来保存提取出来的文件

3. **选择要提取的分区**：
   - 点击"扫描分区"按钮，会自动检测所有可用分区
   - 或者直接在列表中勾选你需要的分区
   - 常用选择：
     - ✅ `boot` 或 `init_boot` - 用于 Root/Magisk
     - ✅ `vendor_boot` - 某些设备需要
     - ✅ `recovery` - 刷入第三方 Recovery
     - ✅ `vbmeta` - 禁用 AVB 验证时需要

4. **开始提取**：
   - 点击"开始提取"按钮
   - 等待完成（日志窗口会显示进度）

5. **完成**：
   - 提取的 `.img` 文件会保存在你选择的输出目录中

## 常见用途示例

### 场景 1：我想 Root 手机（使用 Magisk）

需要提取：
- `init_boot.img`（新设备，如 Android 13+）
- 或 `boot.img`（老设备）

**操作步骤**：
1. 勾选 `init_boot` 或 `boot`
2. 点击"开始提取"
3. 提取出来的 `.img` 文件传到手机
4. 用 Magisk 修补这个文件
5. 用 fastboot 刷入修补后的文件

### 场景 2：我想刷入 TWRP Recovery

需要提取：
- `recovery.img`

**操作步骤**：
1. 勾选 `recovery`
2. 点击"开始提取"
3. 用 fastboot 刷入：`fastboot flash recovery recovery.img`

### 场景 3：我想提取所有分区做备份

**操作步骤**：
1. 点击"扫描分区"
2. 点击"全选"
3. 点击"开始提取"
4. 耐心等待（可能需要较长时间，某些分区很大）

## 常见问题解决

### ❌ 提示找不到 payload-dumper-go 命令

**解决方法**：
```bash
# 重新安装
brew install payload-dumper-go

# 或者检查是否在 PATH 中
which payload-dumper-go
```

### ❌ 提取失败或卡住

**可能原因**：
1. payload.bin 文件损坏 - 重新下载
2. 磁盘空间不足 - 清理磁盘（system 分区可能 2-3GB）
3. 权限问题 - 选择有写入权限的输出目录

### ❌ 点击"浏览..."后程序崩溃

这个 bug 已经修复了，确保使用最新版本的代码。

### ❌ 不知道该提取哪些分区

点击"常用分区"按钮，会自动选择最常用的几个：
- boot
- init_boot
- vendor_boot
- recovery
- vbmeta
- dtbo

## 快捷方式（可选）

如果你经常使用，可以创建一个快捷启动脚本：

1. 创建文件 `start.sh`：
```bash
#!/bin/bash
cd ~/Downloads/payload-extractor-gui
python3 payload_extractor_gui.py
```

2. 添加执行权限：
```bash
chmod +x start.sh
```

3. 以后双击 `start.sh` 就可以启动了！

或者直接在终端输入：
```bash
alias payload='cd ~/Downloads/payload-extractor-gui && python3 payload_extractor_gui.py'
```

然后只需要输入 `payload` 就能启动程序。

## 视频教程（如果还是不会）

考虑录制一个操作视频放在 GitHub，会更直观！

## 需要帮助？

- 提交 Issue 到 GitHub
- 查看 README.md 中的详细说明
- 搜索相关刷机论坛

---

**提示**：第一次使用可能觉得复杂，但实际操作一次后就会很简单了！加油！💪
