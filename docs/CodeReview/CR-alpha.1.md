逻辑耦合处

_无_

[//]: # "- 全局单例 editor 被大量 UI、菜单、toolbar store 直接读取和修改，编辑器生命周期、按钮行为、右键菜单状态耦合在一起：src/stores/editor/instance.ts:3、src/components/editor/EditorCanvas.vue:4、src/stores/"
[//]: # "  btnToolBar/btnFormats/btnBasic.ts:4、src/stores/btnContextMenu/table.ts:4。"
[//]: # '- ContextMenu.vue 用 computed(() => getEditor()?.isActive("table"))，但 getEditor() 不是响应式依赖，菜单类型和编辑器 selection 状态之间存在隐式、不可追踪耦合：src/components/editor/ContextMenu.vue:12。'
[//]: # "- 代码视图依赖 window.editorInstance、window._debugAST、全局 DOM onclick 和 iframe 父子通信，编辑器核心、调试接口、页面按钮被耦合到全局对象：public/code_view/editor.js:461、public/code_view/editor.js:472、"
[//]: # "  public/code_view/index.html:160。"
[//]: # "- Rust parser 写死 site/title/language/page，解析逻辑和当前 SCP/Wikidot 页面元信息耦合：crates/w_parser/src/lib.rs:17。"

代码不规范处

_无_

[//]: # "- 使用 //@ts-ignore 压掉 useEditor 生命周期回调类型问题：src/components/editor/EditorCanvas.vue:37。"
[//]: # "- public/code_view/editor.js 从 CodeMirror 内部路径导入 @codemirror/language/dist/index.js，且 foldEffect 未使用：public/code_view/editor.js:385。"
[//]: # "- index.html 中大量内联 onclick，同时 Tauri 配置关闭 CSP，代码风格和安全边界混在一起：public/code_view/index.html:160、src-tauri/tauri.conf.json:26。"
[//]: # "- completion.js 多处补全片段生成未闭合 Wikidot 标签，例如 [[/tabview、[[/module、[[/html、[[/code 缺少完整闭合：public/code_view/component/completion.js:326、public/code_view/component/completion.js:566、"
[//]: # "  public/code_view/component/completion.js:579、public/code_view/component/completion.js:608。"
[//]: # "- [[user 补全插入的是 [[*user ，但光标位置按 [[#user  计算，字符串和 selection 偏移不一致：public/code_view/component/completion.js:540。"
[//]: # "- 文件/命名存在拼写和大小写不统一问题，例如 varibles.css、divBlock.vue，在跨平台路径大小写敏感环境中容易出问题。"

明显漏洞或风险

1. 右键 Paste 改成 insertText，和普通粘贴保持一致
2. parser 的 println 后面记得关掉，避免内容进日志

[//]: # "- Tauri CSP 被设为 null，同时页面存在内联脚本和全局函数，扩大 XSS/脚本注入后的影响面：src-tauri/tauri.conf.json:26、public/code_view/index.html:209。"
[//]: # '- 代码视图每次文档变更都 postMessage(..., "*")，会把编辑内容发送给任意父窗口来源：public/code_view/editor.js:412。'
[//]: # "- index.html 里的 message 监听没有校验 event.origin，可被任意父/外部窗口投递 h2o2-init 覆盖编辑内容：public/code_view/index.html:237。"
[//]: # '- editor.js 的来源校验只判断 event.origin.endsWith("wikidot.com")，边界过宽，且与 index.html 中另一个无校验监听逻辑不一致：public/code_view/editor.js:478。'
[//]: # "- 右键菜单 Paste 使用 insertContent(text)，而普通粘贴路径使用 insertText(text)；同样是剪贴板文本，两条路径行为不一致，右键粘贴会走 Tiptap 内容解析：src/components/editor/ContextMenu/DefaultContextMenu/"
[//]: # "  Paste.vue:5、src/components/editor/EditorCanvas.vue:42。"
[//]: # "- TextColorExtension、FontSizeExtension 直接把属性拼进 inline style，setEditorTextColor(color: string) 没有约束输入；在 CSP 关闭的环境下，这类样式注入风险更明显：src/stores/editor/extensions/"
[//]: # "  TextColorE.ts:11、src/stores/editor/extensions/FontSizeE.ts:11、src/stores/btnToolBar/btnFormats/btnColor.ts:3。"
[//]: # "- Rust parser 对输入大小没有限制，且会 pretty serialize AST 并返回 HTML+AST；大文本可能造成本地 CPU/内存压力：src-tauri/src/handlers/connect_parser.rs:2、crates/w_parser/src/lib.rs:28、crates/w_parser/src/"
[//]: # "  lib.rs:39。"
[//]: # "- parser 会把完整 AST 和 HTML 打到 stdout，编辑内容可能出现在日志里：crates/w_parser/src/lib.rs:43、crates/w_parser/src/lib.rs:52。"
[//]: # "- 颜色预览点击后按“离当前光标最近的同色值”更新，而不是按被点击 widget 的实际位置；同一颜色多次出现时会改错位置：public/code_view/component/color_preview.js:183。"
