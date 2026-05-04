# SCP Foundation WYSIWYG 编辑器 - 代码审查报告

## 📋 审查范围
- 所有 Python 源代码文件 (不包括 .gitignore 中列出的文件)
- 所有 JavaScript 源代码文件
- 配置文件和导入依赖

---

## 🔴 严重安全问题

### 1. **XSS 漏洞 - innerHTML 直接注入未验证内容**

**位置**: 
- `controllers/js/render_inject.js:4` - `document.getElementById('editor-root').innerHTML = __SAFE_HTML__;`
- `utils/js/insert_html_at_point.js:24` - `template.innerHTML = safeHtml.trim();`
- `ui/css_styles/js/License.js` - 多处使用 innerHTML
- `ui/css_styles/js/footnotes.js:43` - `footer.innerHTML = html;`

**风险**:
虽然使用了 `json.dumps()` 进行基础转义，但仍然存在以下风险：
1. 即使经过 JSON 序列化，恶意构造的 HTML 仍可能通过某些绕过技术执行
2. BeautifulSoup 解析的输出可能包含未完全清理的内容
3. 没有使用专门的 HTML 清理库（如 DOMPurify）

**建议**: 
- 使用 DOMPurify 库或 textContent 替代 innerHTML（如果只需要文本）
- 在服务端对 HTML 进行严格的白名单验证
- 考虑使用 `document.createTextNode()` 或 `textContent` 来避免 HTML 解析

**示例修复**:
```javascript
// 不安全
document.getElementById('editor-root').innerHTML = __SAFE_HTML__;

// 更安全的方式
document.getElementById('editor-root').innerText = __SAFE_TEXT__;
// 或者使用 DOMPurify
document.getElementById('editor-root').innerHTML = DOMPurify.sanitize(__SAFE_HTML__);
```

---

### 2. **URL 注入漏洞 - 链接构建缺乏验证**

**位置**: 
- `controllers/toolbar_controller.py:119` - 直接将用户输入的 URL 嵌入 HTML
```python
html = f'<a href="{url}"{target_attr}>{display_text}</a>'
ui.browser.page().runJavaScript(f"document.execCommand('insertHTML', false, '{html}');")
```

**风险**:
1. 用户可以输入 `javascript:` URL 执行任意 JavaScript
2. 用户可以输入 `data:` URL 携带恶意内容
3. 双引号转义不完整，可能导致 JavaScript 注入

**建议**:
- 验证 URL 协议（只允许 http/https）
- 对特殊字符进行完整转义
- 使用 `urllib.parse.urlparse()` 进行 URL 验证

**示例修复**:
```python
from urllib.parse import urlparse
import json

def validate_url(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ['http', 'https', '']:
            return False
        return True
    except:
        return False

if validate_url(url):
    safe_url = json.dumps(url)
    safe_text = json.dumps(text if text else url)
    html = f'<a href={safe_url} {target_attr}>{safe_text}</a>'
```

---

### 3. **JavaScript 代码注入 - 字符串拼接构建 JavaScript**

**位置**:
- `controllers/MAIN_CONTROLLER.py:96` - `f"window.monoSecurityEnabled = {enabled};"`
- `controllers/MAIN_CONTROLLER.py:100` - `f"window.lineBreakLocked = {locked};"`
- `controllers/toolbar_controller.py:170` - `f"applyFontSize('{size_str}');"`
- `controllers/toolbar_controller.py:120` - `f"document.execCommand('insertHTML', false, '{html}');"`

**风险**:
1. 如果 `enabled`, `locked` 或 `size_str` 包含特殊字符，可能导致 JavaScript 语法错误或注入
2. 没有对这些值进行类型检查或转义

**建议**:
- 使用 JSON 序列化所有动态值
- 避免字符串拼接构建 JavaScript 代码
- 使用参数化的方式传递数据

**示例修复**:
```python
# 不安全
self.browser.page().runJavaScript(f"window.monoSecurityEnabled = {enabled};")

# 更安全
enabled_json = json.dumps(enabled)
self.browser.page().runJavaScript(f"window.monoSecurityEnabled = {enabled_json};")
```

---

### 4. **路径遍历漏洞 - 文件打开缺乏安全验证**

**位置**: 
- `controllers/read_from_desktop.py:18-20` - 只检查 `.txt` 后缀，未检查路径合法性

```python
if not file_path.lower().endswith(".txt"):
    QMessageBox.warning(read_desk, "读取失败", "请选择 .txt 后缀的文本文件！")
    return
```

**风险**:
1. 用户虽然被限制在桌面目录，但可以访问 Desktop 中的任何 `.txt` 文件
2. 如果路径包含 `..` 或符号链接，可能绕过限制（虽然 QFileDialog 可能已防止，但代码本身不安全）
3. 没有大小限制检查，可能导致读取超大文件导致内存溢出

**建议**:
- 验证文件大小限制
- 使用 `os.path.realpath()` 规范化路径
- 验证文件不在允许的目录之外
- 添加文件编码验证

**示例修复**:
```python
import os
import pathlib

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

desktop = os.path.join(os.path.expanduser("~"), "Desktop")
file_path, _ = QFileDialog.getOpenFileName(
    read_desk,
    "选择要读取的 .txt 文件",
    desktop,
    "Text Files (*.txt);;All Files (*)"
)

if not file_path:
    return 

# 安全验证
real_path = os.path.realpath(file_path)
desktop_real = os.path.realpath(desktop)
if not real_path.startswith(desktop_real):
    QMessageBox.warning(read_desk, "读取失败", "文件必须在桌面目录内！")
    return

file_size = os.path.getsize(file_path)
if file_size > MAX_FILE_SIZE:
    QMessageBox.warning(read_desk, "读取失败", f"文件过大（最大 {MAX_FILE_SIZE} 字节）")
    return

try:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
except UnicodeDecodeError:
    QMessageBox.warning(read_desk, "读取失败", "文件编码错误，请使用 UTF-8 编码")
    return
```

---

### 5. **本地资源访问过度权限**

**位置**: 
- `controllers/MAIN_CONTROLLER.py:80-83` - 允许本地文件访问外部资源

```python
settings.setAttribute(
    QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls,
    True
)
```

**风险**:
1. 允许本地 HTML 访问远程资源可能导致信息泄露
2. 如果 HTML 被恶意修改，可能导致加载恶意资源
3. 跨域请求限制被绕过

**建议**:
- 将此设置改为 False，除非有特殊需求
- 如果必须允许，应该实现严格的 CORS 策略
- 使用内容安全策略（CSP）

**示例修复**:
```python
# 改为更安全的配置
settings.setAttribute(
    QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls,
    False  # 禁用跨域访问
)

# 如果需要加载远程资源，使用 https:// URL 而不是本地文件
```

---

## 🟡 待观察问题

### 1. **BeautifulSoup HTML 解析 - 潜在的 ReDoS 攻击**

**位置**:
- `formats/wikidot/wikidot_parser.py:29` - `soup = BeautifulSoup(html, 'html.parser')`
- `formats/wikidot/wikidot_exporter.py:29` - `soup = BeautifulSoup(html, 'html.parser')`
- 多处使用 BeautifulSoup 处理用户输入的 HTML

**风险**:
1. BeautifulSoup 的正则表达式可能易受 ReDoS（正则表达式拒绝服务）攻击
2. 大型恶意构造的 HTML 可能导致解析超时
3. 递归解析可能导致堆栈溢出

**建议**:
- 添加 HTML 大小限制
- 添加解析超时机制
- 使用 `lxml` 而不是 `html.parser`（更快更安全）
- 考虑添加输入大小验证

**示例修复**:
```python
from bs4 import BeautifulSoup

MAX_HTML_SIZE = 50 * 1024 * 1024  # 50MB

def safe_parse_html(html_str):
    if len(html_str) > MAX_HTML_SIZE:
        raise ValueError("HTML 过大")
    try:
        soup = BeautifulSoup(html_str, 'lxml')  # 使用 lxml 更安全
        return soup
    except Exception as e:
        print(f"HTML 解析失败: {e}")
        return None
```

---

### 2. **错误消息泄露信息**

**位置**:
- `controllers/render_controller.py:118` - `print(f"读取渲染 JS 模板失败 ({js_path}): {e}")`
- `controllers/run_insert_js.py:28` - `print(f"读取通用插入 JS 模板失败 ({js_path}): {e}")`
- 多处使用 `print()` 打印完整的文件路径和异常

**风险**:
1. 错误消息可能泄露系统文件结构
2. 异常栈跟踪可能包含敏感信息
3. 路径信息可能帮助攻击者定位文件

**建议**:
- 使用专业的日志库（logging）替代 print()
- 在生产环境中隐藏敏感的错误详情
- 向用户显示通用错误消息，在日志中记录详细信息

**示例修复**:
```python
import logging

logger = logging.getLogger(__name__)

try:
    with open(js_path, 'r', encoding='utf-8') as f:
        js_template = f.read()
except Exception as e:
    logger.error(f"Failed to read JS template: {e}", exc_info=True)
    print("Failed to load template - please contact administrator")
    return None
```

---

### 3. **RegEx 表达式 ReDoS 风险**

**位置**:
- `controllers/scanner/scan_wikidot.py:34` - `RE_DIV = re.compile(r'\[\[\s*div\b.*?\bclass\s*=\s*"([^"]*)"', re.IGNORECASE | re.DOTALL)`
- `formats/wikidot/parse_node/parse_node.py` - 多处复杂的正则表达式

**风险**:
1. DOTALL 标志 + 贪心量词可能导致灾难性回溯
2. 注释 `# 改为非贪婪匹配以避免灾难性回溯` 表明开发者已意识到，但仍有风险
3. 复杂的嵌套正则可能在某些输入下产生 ReDoS

**建议**:
- 使用专门的 HTML 解析库而不是正则表达式
- 在处理用户输入前对大小进行限制
- 定期审查正则表达式的性能
- 使用 regex 库而不是 re 库（提供更好的 ReDoS 防护）

**示例修复**:
```python
import re

# 避免 DOTALL 与贪心量词的组合
# 不安全
RE_DIV_BAD = re.compile(r'\[\[\s*div\b.*?\bclass\s*=\s*"([^"]*)"', re.DOTALL)

# 更安全 - 限制回溯
RE_DIV_SAFE = re.compile(
    r'\[\[\s*div\b[^\]]*?\bclass\s*=\s*"([^"]*)"',
    re.IGNORECASE
)

# 或使用 HTML 解析器
from html.parser import HTMLParser
```

---

### 4. **JSON 注入风险**

**位置**:
- `controllers/menu_controller.py:139` - `matches_json = json.dumps(matches)`
- `controllers/js/render_inject.js` - 使用 `json.dumps()` 处理的数据

**风险**:
1. 虽然 json.dumps() 是安全的，但 Python 到 JavaScript 的转换可能有边界情况
2. 如果 JSON 中包含 Unicode 字符，某些浏览器可能处理不当
3. JSON 中的特殊字符（如 </script>）可能导致 JavaScript 注入

**建议**:
- 在 JavaScript 中使用 JSON.parse() 而不是直接评估
- 始终对特殊字符进行转义
- 验证 JSON 结构

**示例修复**:
```javascript
// 不安全
var data = __JSON_DATA__;  // 直接注入

// 安全
var data = JSON.parse(__JSON_SAFE__);  // 使用 JSON.parse()
// 确保 __JSON_SAFE__ 是有效的 JSON 字符串
```

---

### 5. **缺少 CSRF 保护**

**位置**:
- 整个应用中缺少 CSRF token 验证机制

**风险**:
1. 虽然这是桌面应用而非 Web 应用，但如果集成了 Web 功能，需要 CSRF 保护
2. Python-JavaScript 通信缺少验证令牌

**建议**:
- 如果后续集成 Web 功能，添加 CSRF token
- 使用 SameSite Cookie 属性
- 验证 Origin 和 Referer 头

---

## 🟢 需要改善的地方

### 1. **缺少输入验证框架**

**问题**:
- 没有统一的输入验证机制
- 验证分散在代码各处
- 没有 sanitize/validate 工具类

**建议**:
创建统一的验证模块:
```python
# utils/validators.py
import re
from urllib.parse import urlparse

class InputValidator:
    @staticmethod
    def validate_url(url, allowed_schemes=['http', 'https']):
        try:
            parsed = urlparse(url)
            if parsed.scheme and parsed.scheme not in allowed_schemes:
                return False
            return True
        except:
            return False
    
    @staticmethod
    def validate_filename(filename, max_length=255):
        if len(filename) > max_length:
            return False
        if any(char in filename for char in ['<', '>', ':', '"', '|', '?', '*']):
            return False
        return True
    
    @staticmethod
    def sanitize_html(html, max_size=50*1024*1024):
        if len(html) > max_size:
            raise ValueError("Content too large")
        # 使用 DOMPurify 或其他库进行清理
        return html
```

---

### 2. **缺少认证和授权**

**问题**:
- 没有用户认证机制
- 没有权限检查
- 所有功能都可以访问

**建议**:
- 如果需要多用户支持，添加认证层
- 实现基于角色的访问控制 (RBAC)
- 记录用户操作日志

---

### 3. **日志记录不完善**

**问题**:
- 使用 print() 而不是专业的日志库
- 没有日志级别控制
- 没有日志文件持久化
- 没有日志轮转

**建议**:
```python
# utils/logger.py - 改进版本
import logging
import logging.handlers
import os

def setup_logging(name, log_dir='logs'):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # 文件处理器 - 日志轮转
    os.makedirs(log_dir, exist_ok=True)
    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, f'{name}.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    
    # 控制台处理器 - 生产环境改为 WARNING
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
```

---

### 4. **缺少依赖版本固定**

**位置**: `requirements.txt`

**问题**:
```
PyQt6
PyQt6-WebEngine
requests
beautifulsoup4
pyqt6-sip
```

所有依赖都没有版本号，导致:
1. 无法重现构建
2. 安全补丁应用不一致
3. 依赖冲突风险

**建议**:
使用精确的版本号:
```
PyQt6==6.6.1
PyQt6-WebEngine==6.6.1
requests==2.31.0
beautifulsoup4==4.12.2
pyqt6-sip==13.6.0
lxml==4.9.3
```

运行以下命令生成:
```bash
pip freeze > requirements.txt
```

---

### 5. **缺少类型提示**

**问题**:
- Python 代码缺少类型提示
- 难以进行静态分析
- IDE 自动完成不完美

**建议**:
添加类型提示:
```python
# 不完整
def parse_wikidot_code(code):
    result = {
        "themes": {...}
    }
    return result

# 改进
from typing import Dict, Any

def parse_wikidot_code(code: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "themes": {...}
    }
    return result
```

运行类型检查:
```bash
pip install mypy
mypy --strict .
```

---

### 6. **缺少单元测试**

**问题**:
- 没有发现 test 文件或测试套件
- 没有 CI/CD 测试流程
- 重构风险高

**建议**:
创建测试框架:
```python
# tests/test_validators.py
import pytest
from utils.validators import InputValidator

def test_validate_url_valid():
    assert InputValidator.validate_url("https://example.com")

def test_validate_url_invalid():
    assert not InputValidator.validate_url("javascript:alert('xss')")

def test_validate_filename_invalid():
    assert not InputValidator.validate_filename("file<name>.txt")
```

运行测试:
```bash
pip install pytest
pytest tests/
```

---

### 7. **缺少文档**

**问题**:
- 代码缺少详细的 docstring
- 没有 API 文档
- 没有安全指南

**建议**:
添加详细的文档字符串:
```python
def parse_wikidot_code(code: str) -> Dict[str, Any]:
    """
    解析 Wikidot 源代码并提取元数据。
    
    Args:
        code: Wikidot 格式的源代码字符串
        
    Returns:
        包含以下键的字典:
        - themes: 主题配置
        - better_footnotes: 是否使用更好的脚注
        - rate_module: 评分模块配置
        - css: 提取的 CSS 代码
        - has_toc: 是否包含目录
        
    Raises:
        ValueError: 如果代码无效
        
    Example:
        >>> result = parse_wikidot_code("[[include theme:basalt]]")
        >>> result['themes']['basalt']
        True
    """
```

---

### 8. **硬编码值应使用配置文件**

**位置**:
- `controllers/MAIN_CONTROLLER.py:91-92` - 硬编码延迟时间 2000ms
- `controllers/MAIN_CONTROLLER.py:64` - 硬编码窗口大小

**建议**:
创建配置文件:
```python
# config.py
CONFIG = {
    'UI': {
        'WINDOW_WIDTH': 1400,
        'WINDOW_HEIGHT': 950,
        'INITIAL_DELAY_MS': 2000,
    },
    'LIMITS': {
        'MAX_FILE_SIZE': 100 * 1024 * 1024,
        'MAX_HTML_SIZE': 50 * 1024 * 1024,
    },
    'SECURITY': {
        'ALLOW_REMOTE_ACCESS': False,
        'ALLOWED_URL_SCHEMES': ['http', 'https'],
    }
}
```

---

### 9. **缺少异常处理标准化**

**问题**:
- 异常处理不一致
- 有些地方没有异常处理
- 没有自定义异常类

**建议**:
创建自定义异常:
```python
# exceptions.py

class SCPEditorError(Exception):
    """基础异常类"""
    pass

class ParsingError(SCPEditorError):
    """解析错误"""
    pass

class RenderError(SCPEditorError):
    """渲染错误"""
    pass

class ValidationError(SCPEditorError):
    """验证错误"""
    pass
```

---

### 10. **缺少环境隔离**

**问题**:
- 没有使用虚拟环境
- 依赖全局安装
- 可能导致版本冲突

**建议**:
使用虚拟环境:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

---

## 📊 风险总结

| 类别 | 数量 | 严重程度 |
|------|------|--------|
| 严重安全问题 | 5 | 🔴 高 |
| 待观察问题 | 5 | 🟡 中 |
| 改进建议 | 10 | 🟢 低 |

---

## ✅ 建议优先级

### 立即修复（优先级 1）:
1. ❌ XSS 漏洞 - 使用 DOMPurify 清理 HTML
2. ❌ URL 注入 - 添加 URL 验证
3. ❌ JavaScript 注入 - 使用 JSON 序列化

### 短期修复（优先级 2）:
4. ❌ 路径遍历 - 添加路径验证
5. ❌ 本地资源访问 - 禁用跨域访问
6. ⚠️ 使用 lxml 替代 html.parser

### 中期改进（优先级 3）:
7. ⚠️ 实现统一日志系统
8. ⚠️ 添加单元测试
9. ⚠️ 固定依赖版本
10. ⚠️ 添加类型提示

---

## 📝 检查清单

- [ ] 审查并修复 XSS 漏洞
- [ ] 实现 URL 验证
- [ ] 修复 JavaScript 注入风险
- [ ] 实现路径遍历防护
- [ ] 禁用不必要的跨域访问
- [ ] 添加 HTML 大小限制
- [ ] 改进日志记录
- [ ] 创建统一的错误处理
- [ ] 添加输入验证框架
- [ ] 编写单元测试
- [ ] 固定依赖版本
- [ ] 添加代码文档和类型提示
- [ ] 进行代码审查和安全审计

---

## 🔍 审查完成

**审查日期**: 2026-05-04
**审查范围**: 所有主要 Python 和 JavaScript 源文件
**总计发现**: 20 个问题（5 个严重，5 个待观察，10 个改进建议）

---
