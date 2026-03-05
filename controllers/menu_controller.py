import os
import json
from PyQt6.QtWidgets import QMenu
from PyQt6.QtWebEngineCore import QWebEnginePage

# 导入所有的组件注入器 (因为现在全归菜单模块管了，主模块不再需要它们)
from utils.CSS_INJECTOR import (
    inject_terminal_shortcut, inject_terminal_001, inject_raisa_notice,
    inject_class_warning, inject_foundation_background, inject_o5_command,
    inject_video_record, inject_video_record2, inject_page_note,
    inject_email_template, inject_login_logout
)

# 获取当前文件所在目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def handle_prepare_context_menu(ui, pos):
    """
    触发右键菜单前，先通过 JS 获取光标点所在的组件信息
    """
    js = f"document.elementFromPoint({pos.x()}, {pos.y()}).closest('.scp-component')?.getAttribute('data-type')"
    js_table = f"!!document.elementFromPoint({pos.x()}, {pos.y()}).closest('table.wikidot-table')"
    js_tab_btn = f"!!document.elementFromPoint({pos.x()}, {pos.y()}).classList.contains('tab-btn')"
    js_fn_idx = f"(function(){{ var el = document.elementFromPoint({pos.x()}, {pos.y()}); return el ? Array.from(document.querySelectorAll('.scp-footnote')).indexOf(el.closest('.scp-footnote')) : -1; }})()"
    
    full_js = f"JSON.stringify({{ comp: {js}, table: {js_table}, tabBtn: {js_tab_btn}, fnIdx: {js_fn_idx} }})"
    
    # 拿到结果后，调用内部函数真正展示菜单
    ui.browser.page().runJavaScript(full_js, lambda res: _handle_show_menu(ui, pos, json.loads(res)))


def _handle_show_menu(ui, pos, res):
    """
    根据上一步获取的组件类型，动态构建并展示右键菜单
    """
    menu = QMenu()
    c_type = res.get('comp')
    in_table = res.get('table')
    is_tab_btn = res.get('tabBtn')
    fn_idx = res.get('fnIdx', -1)

    paste_act = menu.addAction("粘贴")
    paste_act.triggered.connect(lambda: ui.browser.page().triggerAction(QWebEnginePage.WebAction.Paste))
    menu.addSeparator()

    if fn_idx != -1:
        menu.addAction("编辑脚注").triggered.connect(lambda: ui.open_footnote_editor(fn_idx))
        menu.addSeparator()

    if c_type:
        if c_type == 'tabview' and is_tab_btn:
            menu.addAction("删除该选项卡").triggered.connect(lambda: ui.browser.page().runJavaScript(
                f"removeTab(document.elementFromPoint({pos.x()}, {pos.y()}))"))
            menu.addSeparator()

        del_act = menu.addAction("删除该组件")
        del_act.triggered.connect(lambda: _handle_remove_component(ui, pos))

        if c_type == 'acs':
            cm = menu.addMenu("修改等级颜色 (主等级)")
            primary_classes = ["Safe", "Euclid", "Keter", "Neutralized", "Pending", "Explained", "Esoteric"]
            for cls in primary_classes:
                act = cm.addAction(cls)
                act.triggered.connect(lambda checked, c=cls: _handle_change_acs_class(ui, pos, c))

            sm = menu.addMenu("设置次要等级")
            secondary_classes = ["Apollyon", "Archon", "Cernunnos", "Hiemal", "Tiamat", "Ticonderoga", "Thaumiel", "None"]
            for cls in secondary_classes:
                act = sm.addAction(cls)
                act.triggered.connect(lambda checked, c=cls: _handle_change_acs_secondary(ui, pos, c))
        
        if c_type not in ['image-block', 'image-block-adv']:
             menu.addSeparator()
             menu.addAction("在下面换行").triggered.connect(lambda: _handle_insert_newline(ui, pos))

    if c_type in ['css-module', 'div-block']:
        menu.addSeparator()
        menu.addAction("快捷代码：终端样式").triggered.connect(lambda: _apply_terminal_shortcut(ui, pos))
        menu.addAction("快捷代码：终端 #001").triggered.connect(lambda: inject_terminal_001(ui.browser.page(), pos.x(), pos.y()))
        menu.addAction("快捷代码：RAISA通知").triggered.connect(lambda: inject_raisa_notice(ui.browser.page(), pos.x(), pos.y()))
        menu.addAction("快捷代码：XXXX级机密").triggered.connect(lambda: inject_class_warning(ui.browser.page(), pos.x(), pos.y()))
        menu.addAction("快捷代码：O5议会命令").triggered.connect(lambda: inject_o5_command(ui.browser.page(), pos.x(), pos.y()))
        menu.addAction("快捷代码：基金会背景").triggered.connect(lambda: inject_foundation_background(ui.browser.page(), pos.x(), pos.y()))
        menu.addAction("快捷代码：视频/音频记录1").triggered.connect(lambda: inject_video_record(ui.browser.page(), pos.x(), pos.y()))
        menu.addAction("快捷代码：视频/音频记录2").triggered.connect(lambda: inject_video_record2(ui.browser.page(), pos.x(), pos.y()))
        menu.addAction("快捷代码：便签纸").triggered.connect(lambda: inject_page_note(ui.browser.page(), pos.x(), pos.y()))
        menu.addAction("快捷代码：登入/登出").triggered.connect(lambda: inject_login_logout(ui.browser.page(), pos.x(), pos.y()))
        menu.addAction("快捷代码：电子邮件模版").triggered.connect(lambda: inject_email_template(ui.browser.page(), pos.x(), pos.y()))

    if in_table:
        t_menu = menu.addMenu("表格操作")
        t_menu.addAction("增加行").triggered.connect(lambda: ui.browser.page().runJavaScript("tableAction('addRow')"))
        t_menu.addAction("删除行").triggered.connect(lambda: ui.browser.page().runJavaScript("tableAction('delRow')"))
        t_menu.addAction("增加列").triggered.connect(lambda: ui.browser.page().runJavaScript("tableAction('addCol')"))
        t_menu.addAction("删除列").triggered.connect(lambda: ui.browser.page().runJavaScript("tableAction('delCol')"))
        t_menu.addAction("向右合并 (删除竖线)").triggered.connect(lambda: ui.browser.page().runJavaScript("tableAction('mergeRight')"))
        t_menu.addAction("隐藏/显示边框").triggered.connect(lambda: ui.browser.page().runJavaScript("tableAction('toggleBorder')"))
        t_menu.addSeparator()
        t_menu.addAction("删除表格").triggered.connect(lambda: ui.browser.page().runJavaScript("tableAction('delTable')"))

    if not c_type and not in_table:
        add_fn = menu.addAction("插入脚注")
        add_fn.triggered.connect(ui.insert_new_footnote)

    menu.exec(ui.browser.mapToGlobal(pos))

# ======== 以下为菜单专属的私有子动作执行函数 ========

def _apply_terminal_shortcut(ui, pos):
    """注入终端快捷代码，并重置相关版式复选框状态"""
    inject_terminal_shortcut(ui.browser.page(), pos.x(), pos.y())
    ui.check_enable_basalt.setChecked(False)
    ui.check_enable_shivering.setChecked(False)
    ui.check_enable_bhl.setChecked(False)
    ui.update_theme_state()

def _handle_insert_newline(ui, pos):
    js_path = os.path.join(CURRENT_DIR, 'js', 'insert_newline.js')
    try:
        with open(js_path, 'r', encoding='utf-8') as f:
            js_template = f.read()
        final_js = js_template.replace('__POS_X__', str(pos.x())).replace('__POS_Y__', str(pos.y()))
        ui.browser.page().runJavaScript(final_js)
    except Exception as e:
        print(f"读取换行 JS 模板失败: {e}")

def _handle_remove_component(ui, pos):
    ui.browser.page().runJavaScript(f"var el = document.elementFromPoint({pos.x()}, {pos.y()}).closest('.scp-component'); if(el) {{ el.remove(); refreshFootnotes(); }}")

def _handle_change_acs_class(ui, pos, class_name):
    ui.browser.page().runJavaScript(f'applyAcsChange(document.elementFromPoint({pos.x()}, {pos.y()}), "{class_name}")')

def _handle_change_acs_secondary(ui, pos, class_name):
    val = "none" if class_name == "None" else class_name
    ui.browser.page().runJavaScript(f'applyAcsSecondary(document.elementFromPoint({pos.x()}, {pos.y()}), "{val}")')