import json
from PyQt6.QtCore import QTimer
from typing import Optional, List, Dict, Any


class SyncEngine:
    """
    负责所有与 QWebEnginePage / CodeMirror 的 JS 交互，以及
    集中管理 _is_pushing_to_cm 的设置/释放逻辑（try/finally + QTimer）。
    挂载在 ui 上的约定：ui._is_pushing_to_cm (bool)
    """

    def __init__(self, ui):
        self.ui = ui

    def page(self):
        """安全获取 QWebEnginePage 或返回 None"""
        try:
            wnd = getattr(self.ui, 'source_editor_window', None)
            if wnd is None:
                return None
            br = getattr(wnd, 'browser', None)
            if br is None:
                return None
            return br.page()
        except Exception:
            return None

    def run_js_safely(self, js_str: str, set_pushing: bool = False, pushing_timeout_ms: int = 500):
        """
        统一执行 page.runJavaScript，并可选在执行前设置 ui._is_pushing_to_cm=True，
        在 finally 中通过 QTimer.singleShot 释放（防止永久卡死）。
        """
        page = self.page()
        if page is None:
            return

        if set_pushing:
            try:
                self.ui._is_pushing_to_cm = True
            except Exception:
                pass

        try:
            try:
                page.runJavaScript(js_str)
            except Exception as e:
                # 记录但不要抛出，调用者不应阻塞主流程
                print(f"[SyncEngine] runJavaScript failed: {e}")
        finally:
            if set_pushing:
                # 无论如何，500ms 后释放标志，避免永久卡死
                QTimer.singleShot(pushing_timeout_ms, lambda: setattr(self.ui, '_is_pushing_to_cm', False))

    def sync_source_to_editor(self, code_content: Optional[str] = None, pushing_timeout_ms: int = 500):
        """
        将 ui.source_display 的内容推送到 CodeMirror（window.syncToEditor）。
        如果 code_content 显式传入则使用该值，否则去 ui.source_display 读取。
        保证在执行 JS 期间设置 ui._is_pushing_to_cm，并在 finally 中释放（QTimer）。
        """
        if getattr(self.ui, 'source_editor_window', None) is None:
            return
        if getattr(self.ui, 'source_display', None) is None:
            print("⚠️ 警告：ui.source_display 不存在")
            return

        if code_content is None:
            code_content = self.ui.source_display.toPlainText()

        safe_content = json.dumps(code_content)

        js_inject = f"""
(function() {{
    var content = {safe_content};
    console.log("🐍 Python->CM 注入，内容长度=" + content.length);
    if (typeof window.syncToEditor === 'function') {{
        window.syncToEditor(content);
    }} else {{
        console.warn("⏳ syncToEditor 尚未就绪，写入 PENDING_CONTENT");
        window.PENDING_CONTENT = content;
    }}
}})();
"""
        # 使用统一的 run_js_safely，且 set_pushing=True 保证 QTimer 释放
        self.run_js_safely(js_inject, set_pushing=True, pushing_timeout_ms=pushing_timeout_ms)

    def inject_after_load(self, code_content: str):
        """
        注入到尚在加载的页面，使用重试机制并在超时后把 PENDING_CONTENT 留在 window 上。
        保持行为与之前的实现：首次注入时将 _is_pushing_to_cm 设为 True，并在 2000ms 后释放。
        """
        page = self.page()
        if page is None:
            return

        safe_content = json.dumps(code_content)
        js_inject = f"""
(function() {{
    var content = {safe_content};
    var MAX_RETRY = 20;
    var INTERVAL = 150;
    var attempt = 0;

    function trySync() {{
        attempt++;
        console.log("🔄 [重试 #" + attempt + "] 检查 syncToEditor...");
        if (typeof window.syncToEditor === 'function') {{
            window.syncToEditor(content);
            console.log("✅ [重试 #" + attempt + "] 同步成功！");
            return;
        }}
        if (attempt < MAX_RETRY) {{
            setTimeout(trySync, INTERVAL);
        }} else {{
            console.error("❌ 重试耗尽，写入 PENDING_CONTENT 兜底");
            window.PENDING_CONTENT = content;
        }}
    }}
    trySync();
}})();
"""

        def do_inject():
            try:
                self.ui._is_pushing_to_cm = True
            except Exception:
                pass
            try:
                page.runJavaScript(js_inject)
            except Exception as e:
                print(f"[SyncEngine] inject_after_load runJavaScript failed: {e}")
            # 最终保护性释放（2 秒）
            QTimer.singleShot(2000, lambda: setattr(self.ui, '_is_pushing_to_cm', False))

        # 尝试绑定 loadFinished，如果可用
        try:
            page.loadFinished.connect(lambda ok: do_inject())
        except Exception:
            pass

        # 300ms 后再触发一次兜底调用（与早先实现一致）
        QTimer.singleShot(300, do_inject)

    def on_cm_content_changed(self, content: str):
        """
        由 JS 侧（bridge）回调触发的回写逻辑：
        - 如果 _is_pushing_to_cm 为 True，则忽略（这是 Python 注入造成的回调）
        - 否则将内容回写到 ui.source_display（阻断信号，保留滚动）
        """
        if getattr(self.ui, '_is_pushing_to_cm', False):
            print("🔁 [防循环] Python 推送期间，跳过 CM→source_display 回写")
            return

        if getattr(self.ui, 'source_display', None) is None:
            return

        if self.ui.source_display.toPlainText() == content:
            return

        print(f"📨 [CM→source_display] 接收 CM 内容，长度={len(content)} 字节")

        self.ui.source_display.blockSignals(True)
        try:
            v = self.ui.source_display.verticalScrollBar().value()
            h = self.ui.source_display.horizontalScrollBar().value()
            self.ui.source_display.setPlainText(content)
            self.ui.source_display.verticalScrollBar().setValue(v)
            self.ui.source_display.horizontalScrollBar().setValue(h)
        finally:
            self.ui.source_display.blockSignals(False)

    def handle_open_source_dialog(self):
        """
        打开/显示 CodeMirror 源码窗体并建立双向绑定（A: source_display -> CM, B: CM -> source_display）。
        该方法在第一次创建 window 时调用 inject_after_load，之后调用 sync_source_to_editor。
        """
        from code_view.main import FoundationEditor

        is_new_window = False

        if not hasattr(self.ui, 'source_editor_window') or self.ui.source_editor_window is None:
            self.ui.source_editor_window = FoundationEditor()
            is_new_window = True

            # A: source_display -> CM
            self.ui.source_display.textChanged.connect(lambda: self.sync_source_to_editor())
            print("✅ [source_dialog] 已绑定 A 向：source_display → CodeMirror")

            # B: CM -> source_display
            self.ui.source_editor_window.bridge.content_changed.connect(lambda content: self.on_cm_content_changed(content))
            print("✅ [source_dialog] 已绑定 B 向：CodeMirror → source_display")

        # 显示窗体并聚焦
        self.ui.source_editor_window.show()
        self.ui.source_editor_window.activateWindow()
        self.ui.source_editor_window.raise_()

        code_content = self.ui.source_display.toPlainText()
        print(f"📤 [source_dialog] 执行初始同步，内容长度={len(code_content)}")

        if is_new_window:
            self.inject_after_load(code_content)
        else:
            self.sync_source_to_editor(code_content)

    def jump_to_matches(self, matches: List[Dict[str, Any]], first_line: Optional[int] = None):
        """
        将 matches 发到前端，优先调用 window.gotoMatchList(matches)，若不存在则回退到 gotoLine(first_line)。
        该方法集中调用 JS，但不设置 _is_pushing_to_cm（跳转与内容写入语义不同）。
        """
        page = self.page()
        if page is None:
            return

        try:
            matches_json = json.dumps(matches)
        except Exception:
            matches_json = "[]"

        js = f"""
try {{
    if (typeof window.gotoMatchList === 'function') {{
        window.gotoMatchList({matches_json});
    }} else if (typeof window.gotoLine === 'function') {{
        window.gotoLine({first_line if first_line is not None else 1});
    }}
}} catch(e) {{
    console.error('scan -> js run error', e);
}}
"""
        # 不设置 set_pushing（跳转不是内容注入），但统一捕获异常
        self.run_js_safely(js, set_pushing=False)
        # 尝试把焦点切过去
        try:
            if getattr(self.ui, 'source_editor_window', None) is not None:
                try:
                    self.ui.source_editor_window.browser.setFocus()
                except Exception:
                    pass
        except Exception:
            pass
