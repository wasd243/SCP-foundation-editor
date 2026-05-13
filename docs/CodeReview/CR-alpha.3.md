# CR-alpha.3 Code Review

## 审查范围

- 已覆盖仓库主要目录（`src/`、`src-tauri/`、`crates/`、配置与文档目录）。
- 按要求**忽略** `public/` 目录。
- 按要求**忽略** `innerHTML` 相关问题。

## 主要问题

| 严重级别   | 问题                          | 证据                                                                                                                    | 影响                                                                                               | 建议                                                                       |
|--------|-----------------------------|-----------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| High   | `tab`/`panel` ID 生成存在冲突风险   | `src/stores/btnContextMenu/TabView/createTabId.ts:4` 与 `src/stores/btnContextMenu/TabView/btnAddTab.ts:27-28`         | `addTab()` 连续两次调用 `Date.now()` 可能在同一毫秒返回相同值，导致 `id` 冲突，破坏 `aria-controls` / `aria-labelledby` 关联 | 用 `crypto.randomUUID()` 或单调递增计数器；至少保证同一次 addTab 内 button/panel 的 ID 必定不同 |
| High   | CodeView 消息通道缺少来源校验         | `src/ipc/Extensions/CodeView/SyncToParser.ts:15-19`                                                                   | 任意 `window.postMessage` 只要构造 `type: "code-view-content-changed"` 即可触发解析并覆写编辑器内容                  | 在监听处校验 `event.origin` 与 `event.source`（仅接受预期 iframe）                     |
| Medium | 右键粘贴与普通粘贴行为不一致              | `src/components/editor/ContextMenu/DefaultContextMenu/Paste.vue:10` vs `src/components/editor/EditorCanvas.vue:42-56` | 右键粘贴走 `insertContent(text)`，普通 Ctrl+V 走 `insertText(text)`；同一输入在两条路径下结果不一致，易产生格式/结构误插入           | 统一为纯文本插入（`insertText`）或明确区分“粘贴纯文本/粘贴富文本”                                 |
| Medium | 编辑内容被直接输出日志                 | `src/ipc/Extensions/CodeView/SyncToParser.ts:20-21`、`crates/w_parser/src/lib.rs:57`                                   | 用户输入与解析输出会进入控制台/stdout，增加隐私泄露风险并污染日志                                                             | 改为可控 debug 日志（仅开发模式开启），生产默认关闭                                            |
| Low    | 通过 `@ts-ignore` 掩盖类型问题      | `src/components/editor/EditorCanvas.vue:37`                                                                           | 类型错误被静默，后续重构时更容易引入回归                                                                             | 为 `useEditor` 生命周期回调补齐类型，移除 `@ts-ignore`                                 |

## 结论

当前主要风险集中在 **消息通道边界** 与 **TabView ID 生成稳定性**。建议优先修复这两项（均为高优先级），其余问题可在同一轮质量修复中一并处理。