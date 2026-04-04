# SCP Foundation Editor (Web Edition)

![License](https://img.shields.io/badge/license-AGPL--3.0-red.svg)
![Version](https://img.shields.io/badge/Version-1.0.0-green.svg)
![Platform](https://img.shields.io/badge/platform-Web%20%7C%20Windows%20%7C%20macOS-blue.svg)
![Language](https://img.shields.io/badge/language-JavaScript-yellow.svg)
![Language](https://img.shields.io/badge/language-CSS-purple.svg)

一个专为 SCP 基金会中文站设计的 Wikidot 语法编辑器，旨在提供流畅的实时编写体验。

## 🚀 特性
- **全平台覆盖**：支持浏览器端及桌面端（Windows/macOS/Linux）。
- **组件集成**：内置对主流社区组件 ACS 和 AIM 的完美支持。
- **现代交互**：基于 CodeMirror 6，集成 One Dark 主题及实时字符统计。

## 📚 引用与鸣谢/Imports

* **AIM (Advanced Information Methodology)** — By *Dr Moned*
    * [查看组件页面](https://scp-wiki.wikidot.com/component:advanced-information-methodology)
* **ACS Animation (Anomaly Classification System)** — By *EstrellaYoshte*
    * [查看组件页面](https://scp-wiki.wikidot.com/component:acs-animation)
* **Peroxide Theme** - By *OxygenNine*
    * [查看版式页面](https://scp-wiki-cn.wikidot.com/theme:peroxide)
* **Icons & Assets**: 本项目使用的图标来源于经典 Minecraft 模组 [Avaritia](https://github.com/SpitefulFox/Avaritia)，由 **SpitefulFox** 创作并以 **MIT License** 授权。
* **Editor Engine**: Powered by [CodeMirror 6](https://codemirror.net/).
## 🛠 构建指南
本项目前端部分使用 `esbuild` 进行模块打包。

---

## 1. 运行环境与解析安全 (Runtime & Parsing Security)
* **纯净编辑器架构**：本工具基于 **CodeMirror 6** 与自定义 **Lezer** AST 解析引擎。本仓库仅提供代码编辑与语法增强功能，**不内置实时预览窗口 (No-Preview Design)**。
* **执行隔离**：由于不具备 HTML 渲染容器，用户编写的任何恶意脚本（包括但不限于 XSS、JS 注入）在本编辑器环境中均仅作为纯文本解析，无法获得执行权，从物理层面上杜绝了编辑器内的脚本攻击。

## 2. 后端交互与负载责任 (Backend & API Liability)
* **透明交互**：本工具不包含任何自动化、隐蔽的后端异步请求。针对第三方接口（如 FTML/Scpper/Wikidot）的所有调用逻辑均由用户显式触发。
* **性能压力免责**：针对 **SCP-8000/9000** 等高递归、超大规模文档的解析压测，本工具已优化 CodeMirror 状态管理，但若因用户操作导致后端服务器出现响应延迟（如 16980ms+ 延迟）或崩溃，相关责任由操作者承担。
* **凭据保护**：本工具不截留、不存储、不转发用户的 Wikidot 登录凭据（Cookies/Tokens）。

## 3. 代码注入与发布风险 (Code Injection & Publication Risk)
* **静态高亮检测**：编辑器的语法高亮与 Linter 仅用于提升编辑体验，不代表对代码安全性的审核。
* **发布责任确认**：用户通过本编辑器编写并最终保存至维基页面的任何代码，其产生的后果（如页面被封禁、触发维基反注入机制等）由用户自行承担。本仓库不对用户生成的任何内容负责。

---

```bash
# 安装依赖
npm install

# 执行打包
npm run build
```

## 🐵 油猴脚本（Tampermonkey）安装与使用

如果你想在 Wikidot 编辑页直接使用本项目的 CodeMirror 编辑器，可以使用仓库中的油猴脚本：

- 脚本文件：`userscript/h2o2-wikidot-editor.user.js`
- 当前默认编辑器地址：`https://wasd243.github.io/SCP-Foundation-editor-web/test.html`

### 安装步骤

1. 在浏览器安装 Tampermonkey（油猴扩展）。
2. 打开 Tampermonkey 仪表盘，新建脚本。
3. 复制 `userscript/h2o2-wikidot-editor.user.js` 全部内容并保存。
4. 打开（或刷新）任意 Wikidot 编辑页，例如：
   - `https://scp-wiki-cn.wikidot.com/xxx/edit/true`
   - `https://scp-wiki-cn.wikidot.com/editor/edit/true`
5. 脚本会自动隐藏原生 textarea，并注入 H2O2 编辑器 iframe。

### 给用户的发布建议

- 若你部署了自己的网页，请修改脚本中的 `EDITOR_URL` 为你的部署地址。
- 上线时建议启用 `event.origin` 校验，防止跨站消息被滥用。
