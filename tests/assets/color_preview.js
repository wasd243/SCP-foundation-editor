// color-preview.js
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
    
    // 设置内联样式，这样CSS可以直接使用
    span.style.cssText = `
      display: inline-block;
      width: 12px;
      height: 12px;
      margin: 0 4px 0 0;
      border: 1px solid #ccc;
      border-radius: 2px;
      background-color: ${this.color};
      vertical-align: middle;
      cursor: pointer;
    `;
    
    // 添加点击事件监听器
    span.addEventListener("click", this.handleClick.bind(this));
    
    return span;
  }

  handleClick(e) {
    e.stopPropagation();
    this.openColorPicker(e.target);
  }

  openColorPicker(element) {
    const color = element.getAttribute("data-color");
    
    // 创建隐藏的颜色选择器输入框
    const picker = document.createElement("input");
    picker.type = "color";
    picker.value = color;
    picker.style.position = "absolute";
    picker.style.opacity = "0";
    picker.style.width = "0";
    picker.style.height = "0";
    picker.style.pointerEvents = "none";
    
    picker.addEventListener("change", (e) => {
      const newColor = e.target.value;
      this.updateColorInEditor(color, newColor, element);
    });
    
    document.body.appendChild(picker);
    picker.click();
    document.body.removeChild(picker);
  }

  updateColorInEditor(oldColor, newColor, element) {
    // 通过自定义事件将信息传递给editor.js
    const event = new CustomEvent("colorChange", {
      detail: {
        oldColor: oldColor,
        newColor: newColor,
        element: element
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
    
    // 在颜色代码前添加预览小部件
    builder.add(
      from,
      from,
      Decoration.widget({
        widget: new ColorPreviewWidget(color),
        side: -1
      })
    );
  }
  
  return builder.finish();
});

// 导出函数用于在editor.js中处理颜色更新
export function setupColorPickerHandler(editorView) {
  window.addEventListener("colorChange", (event) => {
    const { oldColor, newColor, element } = event.detail;
    
    // 找到颜色代码在文档中的位置
    const text = editorView.state.doc.toString();
    const index = text.indexOf(oldColor);
    
    if (index !== -1) {
      // 更新颜色代码
      editorView.dispatch({
        changes: {
          from: index,
          to: index + oldColor.length,
          insert: newColor
        }
      });
    }
  });
}
