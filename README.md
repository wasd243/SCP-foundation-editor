# SCP-foundation-editor
### SCP 基金会中文编辑器

![License](https://img.shields.io/badge/license-GPL_3.0-blue) ![Status](https://img.shields.io/badge/status-Alpha-orange)

这是一个为了方便编写 SCP 基金会中文文档而制作的编辑器。本项目旨在简化编辑流程，提升写作体验。

LICENSE will update to AGPL v3.0 after publish pre-release with ftml code.

协议将会在引用ftml代码测试版发布后更新。

# Projects import
File/Folder name in code: rust_engine
* **ftml** [By SCP Foundation community](https://github.com/scpwiki/ftml)

# 引用的代码
文件名或文件夹名：rust_engine
* **ftml** [SCP 基金会](https://github.com/scpwiki/ftml)
---

###  警告 / Disclaimer

**本项目为纯业余开发，处于早期测试阶段（Alpha），包含不确定因素。**

> [!IMPORTANT]
> **请务必做好数据备份！**
> 
> 在使用本编辑器时，请不要完全依赖自动保存或稳定性。对于重要的文档稿件，请务必在本地和沙盒保留副本。
> 
> 作者无法保证这个编辑器不会出现 bug 或导致数据丢失。使用风险自负。
> 
> 另外，请时刻记得保存沙盒与微调代码，没有办法做到与wikidot渲染器一样。
> 
> 风险提示
> 
> 尽管本软件本身是安全的，但开发者无法保证：
> 
> 用户系统中是否存在其他恶意软件（如系统级木马）对键盘进行监听。
> 
> 用户使用的第三方输入法是否包含数据上传行为。
> 
> 使用本软件即表示您已阅读并理解本声明，并认可本软件在键盘输入处理上的安全性。

###  安全免责声明
**键盘数据记录与收集**

**本软件**不包含**任何键盘记录器（Keylogger）或类似的数据监视功能。**

**无记录：本软件不会记录用户的按键历史、输入频率或任何输入习惯数据。**

**无上传：用户通过键盘输入的任何文字（包括但不限于草稿内容、代码、笔记等）均仅在本地内存中处理，绝不会被上传至任何第三方服务器或开发者的个人服务器。**
关于系统日志与输入法 (macOS/Windows)

**用户可能会在终端或系统控制台中看到有关“输入法（IME）”或“控制循环（RunLoop）”的报错信息（例如 macOS 下的 IMKCFRunLoopWakeUpReliable）。**

**技术解释：此类信息属于 macOS 系统或 GUI 框架（PyQt6）与系统输入法组件通信时的标准系统日志，并非本软件在尝试截取输入。**

**无害性声明：这些日志不涉及任何隐私泄露风险，亦不会将您的输入内容导出给开发者。**
---

###  功能 / Features

*目前支持3种版式，代码最详细的是玄武岩版式，同时支持better footnote 更好的脚注代码生成，可以自定义css，div模块，同时可以一键生成常用css的代码*

* **便捷编辑**：专为 SCP 文档格式优化的编辑体验
* **更多功能**：详见版本更新，不同版本功能更新不同
* **保存txt**：目前使用.txt格式保存生成的wikidot代码，根据左上角三个点图标保存
   <img width="574" height="277" alt="Screenshot 2026-02-21 at 11 38 45 AM" src="https://github.com/user-attachments/assets/2c7ddad9-9c1e-483b-970c-2abad71f5a50" />

* **代码反相解析**：该功能可以用于翻译，但是尚不稳定
* **一键生成**：可以一键生成的代码如下：
  * **ACS**可生成对应的ACS动画和夜琉璃版式适配代码
  * **AIM**可生成对应的上半部分和下半部分代码
  * **CSS和div模块**快捷代码：
    * **终端样式**
    * **终端样式#001**
    * **RAISA通知**
    * **O5议会命令等**
    * 用户可以自行编辑内容，系统会根据其中内容生成对应代码并渲染为类似的格式，用户可以直接编辑其中的内容
     <img width="1470" height="956" alt="Screenshot 2026-02-21 at 11 31 19 AM" src="https://github.com/user-attachments/assets/0bffabb4-2342-41ba-999b-9a49dfff51ab" />
  * **脚注** 可以根据better footnote 自动适配脚注代码
  * **图片块** 两种图片块，支持自定义长宽
  * **Tabview选项卡** 自动生成并编辑Tabview选项卡内容。
  * **授权引用** 自动生成对应的授权引用模块代码，但是连接过长时无法反相解析并渲染，需要手动输入
  * **玄武岩版式专用代码**：
     <img width="1470" height="956" alt="Screenshot 2026-02-21 at 11 37 09 AM" src="https://github.com/user-attachments/assets/0b5a4001-2532-40d6-8d64-3609562f6340" />
     <img width="1470" height="956" alt="Screenshot 2026-02-21 at 11 37 15 AM" src="https://github.com/user-attachments/assets/5c613b22-e53e-421f-8c9f-d13fd3c01659" />
  * **可折叠的模块** [[collapsible show="+ 打开折叠内容" hide="- 关闭折叠内容"]]在这里输入折叠内的内容...[[/collapsible]]
  * **用户标签** 可点击或带头像的用户标签代码
* **一键清理** 可一键清除所有代码
* **更多功能待补充**


---

### ⚖️ 许可证与版权 / License & Copyright

* **所引用css组件的作者**
* **The authors of the CSS conponents**
* **ACS** Woedenaz
* URL: https://scp-wiki-cn.wikidot.com/anomaly-classification-system-guide
* **AIM** Dr Moned
* URL: https://scp-wiki.wikidot.com/component:advanced-information-methodology
* **Basalt** Liryn and Placeholder McD
* URL: https://scp-wiki.wikidot.com/theme:basalt
* **Betterfootnote** EstrellaYoshte
* URL: https://scp-wiki.wikidot.com/component:betterfootnotes
* **ACS Animation** EstrellaYoshte
* URL: https://scp-wiki.wikidot.com/component:acs-animation
* **夜琉璃版式** Flea_ZER0
* URL: https://scp-wiki-cn.wikidot.com/theme:shivering-night
* **Black Highlighter** Woedenaz and Croquembouche
* URL: https://scp-wiki.wikidot.com/theme:black-highlighter-theme
* **Office** Woedenaz
* URL: https://scp-wiki.wikidot.com/theme:scp-offices-theme
* **CSS** aismallard Jerden Lt Flops EstrellaYoshte Deadly Bread Rounderhouse stormbreath Croquembouche Calibold and Dr Hormress
* URL: https://scp-wiki.wikidot.com/scp-style-resource
* 中文链接：https://scp-wiki-cn.wikidot.com/scp-style-resource

**1. 软件代码协议 (GPL v3.0)**
本项目程序代码基于 [GNU General Public License v3.0](LICENSE) 开源。
您可以自由地使用、研究、修改和分发本软件。如果您修改并分发本项目，或者在本项目基础上开发新软件，您的项目也必须以 GPL v3.0 协议开源。

**2. SCP 基金会内容协议 (CC BY-SA 3.0)**
本项目为 SCP 基金会的衍生工具。项目中涉及的 SCP 基金会相关元素、组件版式（如 ACS、AIM 等）均遵循 **CC BY-SA 3.0**（署名-相同方式共享 3.0）协议。
相关内容的原始版权归原作者及 [SCP 基金会](http://scp-wiki-cn.wikidot.com/) 社区所有。

---
