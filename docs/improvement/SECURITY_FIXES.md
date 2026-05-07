# 安全修复优先级指南

## 🚨 关键安全修复

### 1. XSS 防护 - 使用 DOMPurify

**影响范围**: render_inject.js, insert_html_at_point.js, 多个 UI 组件

```html
<!-- 在 editor.html 中添加 -->
<script src="https://cdn.jsdelivr.net/npm/dompurify@3.0.6/dist/purify.min.js"></script>
```

```javascript
// 替换所有的 innerHTML 使用
// 旧的代码:
document.getElementById('editor-root').innerHTML = __SAFE_HTML__;

// 新的代码:
const cleanHTML = DOMPurify.sanitize(__SAFE_HTML__);
document.getElementById('editor-root').innerHTML = cleanHTML;
```

**预期效果**: 防止 XSS 攻击，清理恶意 HTML 标签和属性

---

### 2. URL 验证 - 创建验证工具

**文件**: `utils/url_validator.py` (新建)

```python
from urllib.parse import urlparse

def validate_url(url: str, allowed_schemes: list = None) -> bool:
    """
    验证 URL 的合法性
    
    Args:
        url: 要验证的 URL
        allowed_schemes: 允许的 URL 方案，默认为 ['http', 'https']
    
    Returns:
        URL 是否有效
    """
    if allowed_schemes is None:
        allowed_schemes = ['http', 'https', '']
    
    try:
        parsed = urlparse(url)
        
        # 检查方案
        if parsed.scheme and parsed.scheme not in allowed_schemes:
            return False
        
        # 防止 javascript: 协议
        if parsed.scheme in ['javascript', 'data', 'vbscript']:
            return False
        
        # 基本验证
        if not url or url.strip() == '':
            return False
        
        return True
    except Exception:
        return False

def sanitize_url(url: str) -> str:
    """对 URL 进行转义"""
    import json
    return json.dumps(url)
```

**修改文件**: `controllers/toolbar_controller.py`

```python
# 替换第 112-120 行
from utils.url_validator import validate_url, sanitize_url
import json

def handle_open_link_dialog(ui):
    dialog = LinkDialog(ui)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        url, text, new_window = dialog.get_data()
        
        # 验证 URL
        if not validate_url(url):
            QMessageBox.warning(ui, "无效的 URL", "请输入有效的 HTTP/HTTPS 链接")
            return
        
        display_text = text if text else url
        target_attr = ' target="_blank"' if new_window else ''
        
        # 安全的 HTML 构建
        safe_url = json.dumps(url)
        safe_text = json.dumps(display_text)
        
        js_code = f"""
        (function() {{
            const link = document.createElement('a');
            link.href = {safe_url};
            link.textContent = {safe_text};
            if ({json.dumps(new_window)}) link.target = '_blank';
            
            const sel = window.getSelection();
            if (sel.rangeCount) {{
                const range = sel.getRangeAt(0);
                range.deleteContents();
                range.insertNode(link);
                range.setStartAfter(link);
                range.collapse(true);
                sel.removeAllRanges();
                sel.addRange(range);
            }}
        }})();
        """
        
        ui.browser.page().runJavaScript(js_code)
```

---

### 3. 路径遍历防护

**修改文件**: `controllers/read_from_desktop.py`

```python
import os
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QTabWidget

def read_from_desktop(read_desk):
    """读取桌面上的 .txt 文件"""
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    
    file_path, _ = QFileDialog.getOpenFileName(
        read_desk,
        "选择要读取的 .txt 文件",
        desktop,
        "Text Files (*.txt);;All Files (*)"
    )
    
    if not file_path:
        return
    
    # 安全验证 1: 检查文件扩展名
    if not file_path.lower().endswith(".txt"):
        QMessageBox.warning(read_desk, "读取失败", "请选择 .txt 后缀的文本文件！")
        return
    
    # 安全验证 2: 路径规范化和验证
    try:
        real_path = os.path.realpath(file_path)
        desktop_real = os.path.realpath(desktop)
        
        # 防止目录遍历
        if not real_path.startswith(desktop_real):
            QMessageBox.warning(read_desk, "读取失败", "文件必须在桌面目录内！")
            return
    except Exception as e:
        QMessageBox.warning(read_desk, "读取失败", f"路径验证失败: {str(e)}")
        return
    
    # 安全验证 3: 文件大小限制
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    try:
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            QMessageBox.warning(
                read_desk, 
                "读取失败", 
                f"文件过大（当前 {file_size // 1024 // 1024}MB，最大 {MAX_FILE_SIZE // 1024 // 1024}MB）"
            )
            return
    except Exception as e:
        QMessageBox.warning(read_desk, "读取失败", f"无法检查文件大小: {str(e)}")
        return
    
    # 读取文件
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        read_desk.source_display.setPlainText(content)
        read_desk.render_to_editor()
        read_desk.centralWidget().findChild(QTabWidget).setCurrentIndex(0)
        QMessageBox.information(
            read_desk, 
            "读取成功", 
            f"文件内容已成功加载并渲染：\n{file_path}\n（注：复杂代码结构可能无法完全还原在UI中）"
        )
    except UnicodeDecodeError:
        QMessageBox.warning(read_desk, "读取失败", "文件编码错误，请使用 UTF-8 编码")
    except Exception as e:
        QMessageBox.warning(read_desk, "读取失败", f"读取文件时发生错误：{str(e)}")
```

---

### 4. 禁用跨域资源访问

**修改文件**: `controllers/MAIN_CONTROLLER.py`

```python
# 替换第 78-83 行
# 允许本地文件访问外部资源
settings = self.browser.settings()

# 改为更安全的配置 - 禁用本地文件访问远程资源
settings.setAttribute(
    QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls,
    False  # 改为 False
)

# 如果需要加载远程资源，使用 https:// URL
settings.setAttribute(
    QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls,
    True  # 仅允许访问本地文件
)
```

---

### 5. 改进日志系统

**新建文件**: `utils/secure_logger.py`

```python
import logging
import logging.handlers
import os
from datetime import datetime

def setup_secure_logging(name: str, log_dir: str = 'logs') -> logging.Logger:
    """
    设置安全的日志系统
    
    Args:
        name: 日志记录器名称
        log_dir: 日志目录
    
    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # 清空现有处理器
    logger.handlers = []
    
    # 创建日志目录
    os.makedirs(log_dir, exist_ok=True)
    
    # 文件处理器 - 日志轮转（每天一个文件，最多保留 30 天）
    log_file = os.path.join(log_dir, f'app-{datetime.now().strftime("%Y-%m-%d")}.log')
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=30  # 保留 30 个备份
    )
    file_handler.setLevel(logging.DEBUG)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # 仅显示 INFO 及以上
    
    # 格式化
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    file_handler.setFormatter(detailed_formatter)
    console_handler.setFormatter(simple_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# 使用示例
logger = setup_secure_logging('scp_editor')
```

**修改现有日志调用**:

```python
# 替换旧的 print() 调用
# 旧的:
print(f"读取渲染 JS 模板失败 ({js_path}): {e}")

# 新的:
logger.error(f"Failed to read template", exc_info=True)
logger.info(f"User performed action: render_to_editor")
```

---

### 6. 配置文件系统

**新建文件**: `config.py`

```python
"""
应用配置文件
"""

CONFIG = {
    # UI 配置
    'UI': {
        'WINDOW_WIDTH': 1400,
        'WINDOW_HEIGHT': 950,
        'THEME': 'default',
        'INITIAL_DELAY_MS': 2000,
    },
    
    # 安全限制
    'LIMITS': {
        'MAX_FILE_SIZE': 100 * 1024 * 1024,  # 100MB
        'MAX_HTML_SIZE': 50 * 1024 * 1024,   # 50MB
        'MAX_CSS_SIZE': 10 * 1024 * 1024,    # 10MB
        'MAX_FILENAME_LENGTH': 255,
    },
    
    # 安全设置
    'SECURITY': {
        'ALLOW_REMOTE_ACCESS': False,
        'ALLOWED_URL_SCHEMES': ['http', 'https'],
        'ENABLE_DEBUG_LOGGING': False,
        'SANITIZE_HTML': True,
    },
    
    # 日志设置
    'LOGGING': {
        'LEVEL': 'INFO',
        'LOG_DIR': 'logs',
        'MAX_BACKUP_COUNT': 30,
        'MAX_LOG_SIZE': 10 * 1024 * 1024,
    }
}

def get_config(key: str, default=None):
    """获取配置值"""
    keys = key.split('.')
    value = CONFIG
    for k in keys:
        if isinstance(value, dict):
            value = value.get(k, default)
        else:
            return default
    return value
```

---

## 📋 修复验证清单

修复完成后，请按照以下清单验证:

- [ ] 使用 DOMPurify 清理所有 innerHTML 输入
- [ ] URL 验证工作正常（测试 javascript: 等恶意 URL）
- [ ] 路径验证防止目录遍历
- [ ] 文件大小限制有效
- [ ] 日志系统记录安全事件
- [ ] 没有敏感信息在日志中泄露
- [ ] 配置文件集中管理
- [ ] 单元测试通过

---

## 🧪 测试用例

### XSS 测试
```html
<!-- 应该被 DOMPurify 清理 -->
<img src=x onerror="alert('XSS')">
<svg onload="alert('XSS')">
<script>alert('XSS')</script>
```

### URL 测试
```
javascript:alert('XSS')  <!-- 应该被拒绝 -->
data:text/html,<script>alert('XSS')</script>  <!-- 应该被拒绝 -->
https://example.com  <!-- 应该接受 -->
http://example.com  <!-- 应该接受 -->
```

### 路径遍历测试
```
/home/user/Desktop/../../../etc/passwd  <!-- 应该被拒绝 -->
C:\Desktop\..\..\windows\system32  <!-- 应该被拒绝 -->
```

---

## 📚 参考资源

- [OWASP 前十](https://owasp.org/www-project-top-ten/)
- [XSS 防护指南](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [DOMPurify 文档](https://github.com/cure53/DOMPurify)
- [PyQt6 安全最佳实践](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Python 安全编码指南](https://python.readthedocs.io/en/latest/library/security_warnings.html)

---
