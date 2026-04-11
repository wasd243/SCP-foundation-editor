// color-preview.js - 改进版
import { EditorView, Decoration, WidgetType } from "@codemirror/view";
import { RangeSetBuilder } from "@codemirror/state";

// 创建颜色预览小部件（放在颜色代码前面）
class ColorPreviewWidget extends WidgetType {
  constructor(color) {
    super();
    this.color = color;
  }

  eq(other) {
    return other.color === this.color;
  }

  toDOM() {
    const span = document.createElement("span");
    span.className = "cm-color-preview";
    span.setAttribute("data-color", this.color);
    span.title = `点击修改颜色: ${this.color}`;
    
    // 设置内联样式，这样CSS可以直接使用
    span.style.cssText = `
      display: inline-block;
      width: 14px;
      height: 14px;
      margin: 0 6px 0 2px;
      border: 1px solid #555;
      border-radius: 3px;
      background-color: ${this.color};
      vertical-align: middle;
      cursor: pointer;
      transition: all 0.2s ease;
      box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    `;
    
    // 添加点击事件监听器
    span.addEventListener("click", this.handleClick.bind(this));
    
    // 添加鼠标悬停效果
    span.addEventListener("mouseenter", () => {
      span.style.transform = "scale(1.1)";
      span.style.borderColor = "#888";
    });
    
    span.addEventListener("mouseleave", () => {
      span.style.transform = "scale(1)";
      span.style.borderColor = "#555";
    });
    
    return span;
  }

  handleClick(e) {
    e.stopPropagation();
    e.preventDefault();
    this.openColorPicker(e.target);
  }

  openColorPicker(element) {
    const color = element.getAttribute("data-color");
    
    // 创建颜色选择器输入框
    const picker = document.createElement("input");
    picker.type = "color";
    picker.value = color;
    picker.style.position = "fixed";
    picker.style.left = "0";
    picker.style.top = "0";
    picker.style.width = "0";
    picker.style.height = "0";
    picker.style.opacity = "0";
    picker.style.pointerEvents = "none";
    
    picker.addEventListener("change", (e) => {
      const newColor = e.target.value;
      this.updateColorInEditor(color, newColor, element);
      // 清理
      document.body.removeChild(picker);
    });
    
    picker.addEventListener("blur", () => {
      // 延迟移除，避免在change事件之前被移除
      setTimeout(() => {
        if (document.body.contains(picker)) {
          document.body.removeChild(picker);
        }
      }, 100);
    });
    
    document.body.appendChild(picker);
    picker.focus();
    picker.click();
  }

  updateColorInEditor(oldColor, newColor, element) {
    // 通过自定义事件将信息传递给editor.js
    const event = new CustomEvent("colorChange", {
      detail: {
        oldColor: oldColor,
        newColor: newColor,
        element: element,
        timestamp: Date.now()
      }
    });
    window.dispatchEvent(event);
  }
}

// 颜色高亮和预览扩展
export const colorPreviewExtension = EditorView.decorations.of((view) => {
  const builder = new RangeSetBuilder();
  const text = view.state.doc.toString();
  
  // 匹配16进制颜色代码
  const hexColorRegex = /#([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b/g;
  let match;
  
  while ((match = hexColorRegex.exec(text)) !== null) {
    const color = match[0];
    const from = match.index;
    const to = from + color.length;
    
    // 避免重复添加小部件（检查是否已经有一个颜色预览）
    // 我们可以检查前面的位置是否已经有小部件
    const line = view.state.doc.lineAt(from);
    const lineText = line.text;
    const colorIndexInLine = from - line.from;
    
    // 如果颜色前面已经有预览小部件，跳过
    if (colorIndexInLine > 0) {
      const beforeColor = lineText.substring(0, colorIndexInLine);
      if (beforeColor.trim().endsWith('cm-color-preview')) {
        continue;
      }
    }
    
    // 在颜色代码前添加预览小部件
    builder.add(
      from,
      from,
      Decoration.widget({
        widget: new ColorPreviewWidget(color),
        side: -1,
        block: false
      })
    );
  }
  
  return builder.finish();
});

// 导出函数用于在editor.js中处理颜色更新
export function setupColorPickerHandler(editorView) {
  window.addEventListener("colorChange", (event) => {
    const { oldColor, newColor, element } = event.detail;
    
    if (!editorView || !editorView.state) {
      console.error('编辑器视图未初始化');
      return;
    }
    
    // 找到颜色代码在文档中的位置（精确查找）
    const text = editorView.state.doc.toString();
    
    // 使用正则表达式查找所有匹配的位置
    const regex = new RegExp(oldColor.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g');
    let match;
    const matches = [];
    
    while ((match = regex.exec(text)) !== null) {
      matches.push({
        index: match.index,
        length: match[0].length
      });
    }
    
    if (matches.length === 0) {
      console.warn(`未找到颜色代码: ${oldColor}`);
      return;
    }
    
    // 尝试确定是哪个匹配项（通常是最接近光标位置的）
    const selection = editorView.state.selection.main;
    const cursorPos = selection.head;
    
    // 找到最接近光标的匹配项
    let bestMatch = matches[0];
    let minDistance = Math.abs(bestMatch.index - cursorPos);
    
    for (const match of matches) {
      const distance = Math.abs(match.index - cursorPos);
      if (distance < minDistance) {
        minDistance = distance;
        bestMatch = match;
      }
    }
    
    // 更新颜色代码
    editorView.dispatch({
      changes: {
        from: bestMatch.index,
        to: bestMatch.index + bestMatch.length,
        insert: newColor
      },
      // 保持光标位置
      selection: editorView.state.selection
    });
    
    // 更新预览小部件的颜色
    if (element && element.style) {
      element.style.backgroundColor = newColor;
      element.setAttribute('data-color', newColor);
      element.title = `点击修改颜色: ${newColor}`;
    }
  });
}

// 导出辅助函数
export function getAllColorsFromText(text) {
  const colors = [];
  const hexColorRegex = /#([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b/g;
  let match;
  
  while ((match = hexColorRegex.exec(text)) !== null) {
    colors.push({
      color: match[0],
      index: match.index,
      length: match[0].length
    });
  }
  
  return colors;
}
