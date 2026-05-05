# Rust 引擎迁移代码审查 - v2.1.0-beta.2
## 拦截器逻辑从 Python 迁移至 Rust

NM这个自动CR机器人提示词没弄好给我一大堆没用的建议——wasd243

**审查日期**: 2026-05-04  
**项目**: SCP Foundation WYSIWYG 编辑器  
**范围**: `engine/rust_engine/ftml_client_py/` 模块  
**版本**: v2.1.0-beta.2

---

## 🔴 严重问题


### 5. **字符串操作 - 潜在的索引越界**

已修复，增加了
```rust
if start_pos >= txt.len() {
        println!("[PARSER] start_pos >= txt.len()");
        return None;
    }
```
用于检测越界

---

### 9. **HTML 输出 - XSS 漏洞**

**位置**: 所有 render 函数

```rust
// collapsible/render.rs:6-8
format!(
    r#"<div class="scp-component collapsible-box" data-type="collapsible" contenteditable="false">
    {show_text}  // ❌ 直接插入，未转义
    {hide_text}  // ❌ 直接插入，未转义
    </div>"#,
)
```

**风险**:
- 用户输入的 HTML 特殊字符可能导致 XSS
- 例如: `show_text = "</div><script>alert('XSS')</script><div>"`
- 无 HTML 转义

**建议**:
```rust
fn escape_html(text: &str) -> String {
    text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\"", "&quot;")
        .replace("'", "&#39;")
}

pub fn render_html(data: &CollapsibleData, inner_html: &str) -> String {
    format!(
        r#"<div class="scp-component collapsible-box" data-type="collapsible" contenteditable="false">
        <div class="collapsible-header">
            <span class="title-label">显示标题: </span>
            <span class="collapsible-show-title title-input" data-field="show" contenteditable="true">{show_text}</span>
        </div>
        <div class="collapsible-content-area" contenteditable="true">{inner_html}</div>
        </div>"#,
        show_text = escape_html(&data.show_text),
        hide_text = escape_html(&data.hide_text),
        inner_html = escape_html(inner_html)
    )
}
```

或使用已有的 HTML escape 库:
```toml
[dependencies]
html-escape = "0.2"
```

```rust
use html_escape::encode_text;

format!(
    r#"<div>...{show_text}...</div>"#,
    show_text = encode_text(&data.show_text)
)
```

**修复优先级**: 🔴 **立即** (安全)

---

## 📋 修复优先级总结

### 🔴 立即修复 (Critical)
3. ✅ 字符串切片越界风险
4. ✅ HTML 转义 XSS 漏洞


### 🟢 中期改进 (Medium)
9. ✅ 性能优化
10. ✅ 文档完善
11. ✅ 测试覆盖
12. ✅ 日志系统

---

## 🔧 修复清单

- [ ] 实现 HTML 转义函数
- [ ] 实现错误类型定义
- [ ] 添加日志系统

---

## 审查者备注

已手动清理所有CR机器人产出的过度工程化建议

---

**审查完成时间**: 2026-05-04  
**审查人员**: wasd243