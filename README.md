# SCP Foundation Editor
### SCP 基金会中文文档编辑器

> 一个用于编写 **SCP Wikidot 文档** 的辅助编辑器，旨在简化 SCP 文档的编辑流程并提升写作体验。

![License](https://img.shields.io/badge/license-AGPL_3.0-blue)
![Status](https://img.shields.io/badge/status-Beta-green)

---

# Import
File/Folder name in code: `rust_engine`

* **ftml** – By SCP Foundation community  
https://github.com/scpwiki/ftml

---

# 引用的代码
文件名或文件夹名：`rust_engine`

* **ftml** – SCP 基金会社区  
https://github.com/scpwiki/ftml

---

# 目录 / TOC

- [项目简介](#项目简介)
- [警告 / Disclaimer](#警告--disclaimer)
- [安全免责声明](#安全免责声明)
- [功能 / Features](#功能--features)
- [下载 / Download](#下载--download)
- [许可证与版权](#️许可证与版权--license--copyright)

---

# 项目简介

这是一个为了方便编写 **SCP 基金会中文文档** 而制作的编辑器。  

本项目旨在通过自动化工具与可视化组件，帮助作者更高效地编写符合 **Wikidot 格式** 的 SCP 文档。

目前项目仍处于 **Beta 阶段**，部分功能仍在开发与优化中。

---

# 警告 / Disclaimer

> [!IMPORTANT]  
> **本项目为业余开发项目，目前处于测试阶段（Beta），仍可能存在不稳定因素。**

请务必做好数据备份。

在使用本编辑器时，请不要完全依赖自动保存或稳定性。  
对于重要的文档稿件，请务必在 **本地和 Wikidot 沙盒中保留副本**。

作者无法保证该编辑器不会出现 bug 或导致数据丢失。  
使用风险由用户自行承担。

此外：

- 请随时保存沙盒内容
- 请保留原始代码备份
- 本编辑器的渲染效果 **无法完全保证与 Wikidot 官方渲染器一致**

---

# 安全免责声明

## 键盘数据记录与收集

**本软件不包含任何键盘记录器（Keylogger）或类似的数据监视功能。**

### 无记录

本软件不会记录：

- 用户按键历史
- 输入频率
- 输入习惯
- 草稿内容

### 无上传

用户通过键盘输入的任何内容（包括草稿、代码或笔记）  
均仅在 **本地内存中处理**，不会上传至任何服务器。

---

# 关于系统日志与输入法 (macOS / Windows)

在部分情况下，用户可能会在系统终端或控制台看到类似以下日志：
IMKCFRunLoopWakeUpReliable

## 技术解释

该日志属于 **macOS 系统输入法组件** 或 **GUI 框架（PyQt6）**  
在与系统输入法通信时产生的标准系统日志。

## 无害性声明

这些日志：

- 不涉及任何键盘监听
- 不包含用户输入内容
- 不会上传至开发者

---

# 功能 / Features

目前支持 **三种版式**，其中 **玄武岩版式（Basalt）** 的支持最完整。

同时支持 **Better Footnote 脚注生成、CSS 模块生成以及常用组件代码自动生成**。

---

# 编辑功能

### 便捷编辑
专为 SCP 文档格式优化的编辑体验。

### 代码反向解析
可将部分 Wikidot 代码反解析为编辑内容（实验性功能）。

---

# 文件管理

### TXT 保存

当前版本使用 `.txt` 文件保存生成的 Wikidot 代码。

保存方式：

- 点击左上角菜单
- 选择保存

---

# 自动生成代码

可一键生成常见 SCP Wiki 组件代码。

---

## ACS（Anomaly Classification System）

生成 ACS 分类系统代码，并支持：

- ACS 动画
- 夜琉璃版式适配

---

## AIM（Advanced Information Methodology）

自动生成：

- 上半部分代码
- 下半部分代码

---

# 快捷 CSS / Div 模块

可一键生成常见 SCP Wiki UI 组件：

- 终端样式
- 终端样式 #001
- RAISA 通知
- O5 议会命令

用户可以直接编辑内容，系统会自动生成对应代码并渲染。

<details>
<summary><b>快捷代码参考图片</b></summary>

<img width="1470" height="956" src="https://github.com/user-attachments/assets/0bffabb4-2342-41ba-999b-9a49dfff51ab"/>

</details>

---

# 脚注系统

支持 **原版脚注预览 / 编辑** 以及  
**Better Footnote 自动生成脚注代码**。

---

# 图片模块

提供 **两种图片块组件**：

- 可自定义宽度
- 可自定义高度

---

# Tabview 选项卡

自动生成并编辑 **Tabview 组件** 内容。

---

# 授权引用模块

自动生成 SCP Wiki 常用的 **授权引用模块代码**。

⚠️ 当链接过长时，反向解析可能失败，需要手动输入。

---

# 玄武岩版式专用模块

提供 **Basalt 版式专用代码生成**。

<details>
<summary><b>玄武岩版式参考图片</b></summary>

<img width="1470" height="956" src="https://github.com/user-attachments/assets/0b5a4001-2532-40d6-8d64-3609562f6340"/>

<img width="1470" height="956" src="https://github.com/user-attachments/assets/5c613b22-e53e-421f-8c9f-d13fd3c01659"/>

</details>

---

# 其他组件

支持生成：

- **Collapsible 折叠模块**

示例：

[[collapsible show="+ 打开折叠内容" hide="- 关闭折叠内容"]]
内容
[[/collapsible]]

---

# 用户标签

支持：

- 可点击用户标签
- 带头像用户标签

---

# 工具功能

- **一键清理代码**  
  清除当前编辑器中的所有代码

- **更多功能正在开发中**

---

# UI 示例

<details>
<summary><b>UI 参考图片</b></summary>

<img width="574" height="277" src="https://github.com/user-attachments/assets/2c7ddad9-9c1e-483b-970c-2abad71f5a50"/>

</details>

---

# ⏬ 下载 / Download

点击右侧 **Release** 下载最新 **Beta 版本**。

当前版本仍需要大量 **Bug 反馈与测试** 才能推进正式版发布。  
非常感谢您的测试与反馈。

---

# ⚖️ 许可证与版权 / License & Copyright

## 软件代码协议

本项目程序代码基于 **GNU AGPL v3.0** 开源。

您可以：

- 使用
- 修改
- 分发

若基于本项目开发新的软件并发布，必须同样遵循 **AGPL v3.0** 协议。

---

## SCP 基金会内容协议

本项目为 **SCP 基金会社区的衍生工具**。

涉及的组件与版式（如 ACS、AIM 等）遵循：

**CC BY-SA 3.0**

原始版权归 **原作者及 SCP 基金会社区** 所有。

---

# 所引用组件作者

**ACS** — Woedenaz  
https://scp-wiki-cn.wikidot.com/anomaly-classification-system-guide

**AIM** — Dr Moned  
https://scp-wiki.wikidot.com/component:advanced-information-methodology

**Basalt** — Liryn / Placeholder McD  
https://scp-wiki.wikidot.com/theme:basalt

**BetterFootnote** — EstrellaYoshte  
https://scp-wiki.wikidot.com/component:betterfootnotes

**ACS Animation** — EstrellaYoshte  
https://scp-wiki.wikidot.com/component:acs-animation

**夜琉璃版式** — Flea_ZER0  
https://scp-wiki-cn.wikidot.com/theme:shivering-night

**Black Highlighter** — Woedenaz / Croquembouche  
https://scp-wiki.wikidot.com/theme:black-highlighter-theme

**Office Theme** — Woedenaz  
https://scp-wiki.wikidot.com/theme:scp-offices-theme

**SCP Style Resource**

https://scp-wiki.wikidot.com/scp-style-resource  
https://scp-wiki-cn.wikidot.com/scp-style-resource
