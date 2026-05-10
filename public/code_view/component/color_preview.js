// color-preview.js - improved version
import { EditorView, Decoration, WidgetType } from "@codemirror/view";
import { RangeSetBuilder } from "@codemirror/state";

// Create a color preview widget (inserted before color code)
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
    span.title = `Click to change color: ${this.color}`;
    
    // Set inline style so CSS can use the value directly
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
    
    // Add click listener
    span.addEventListener("click", this.handleClick.bind(this));
    
    // Add hover effect
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
    
    // Create a color picker input
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
      // Cleanup
      document.body.removeChild(picker);
    });
    
    picker.addEventListener("blur", () => {
      // Delay removal so it doesn't happen before the change event
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
    // Pass data to editor.js via a custom event
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

// Color highlighting and preview extension
export const colorPreviewExtension = EditorView.decorations.of((view) => {
  const builder = new RangeSetBuilder();
  const text = view.state.doc.toString();
  
  // Match hex color codes
  const hexColorRegex = /#([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b/g;
  let match;
  
  while ((match = hexColorRegex.exec(text)) !== null) {
    const color = match[0];
    const from = match.index;
    const to = from + color.length;
    
    // Avoid duplicate widgets (check whether a preview already exists)
    // Check whether a widget is already present before this token
    const line = view.state.doc.lineAt(from);
    const lineText = line.text;
    const colorIndexInLine = from - line.from;
    
    // Skip if there is already a preview widget before this color
    if (colorIndexInLine > 0) {
      const beforeColor = lineText.substring(0, colorIndexInLine);
      if (beforeColor.trim().endsWith('cm-color-preview')) {
        continue;
      }
    }
    
    // Add a preview widget before the color code
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

// Export helper used by editor.js to handle color updates
export function setupColorPickerHandler(editorView) {
  window.addEventListener("colorChange", (event) => {
    const { oldColor, newColor, element } = event.detail;
    
    if (!editorView || !editorView.state) {
      console.error('Editor view is not initialized');
      return;
    }
    
    // Find exact positions of this color code in the document
    const text = editorView.state.doc.toString();
    
    // Use regex to find every matching position
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
      console.warn(`Color code not found: ${oldColor}`);
      return;
    }
    
    // Identify the best match (usually nearest to cursor position)
    const selection = editorView.state.selection.main;
    const cursorPos = selection.head;
    
    // Pick the match closest to the cursor
    let bestMatch = matches[0];
    let minDistance = Math.abs(bestMatch.index - cursorPos);
    
    for (const match of matches) {
      const distance = Math.abs(match.index - cursorPos);
      if (distance < minDistance) {
        minDistance = distance;
        bestMatch = match;
      }
    }
    
    // Update the color code
    editorView.dispatch({
      changes: {
        from: bestMatch.index,
        to: bestMatch.index + bestMatch.length,
        insert: newColor
      },
      // Preserve cursor position
      selection: editorView.state.selection
    });
    
    // Update preview widget color
    if (element && element.style) {
      element.style.backgroundColor = newColor;
      element.setAttribute('data-color', newColor);
      element.title = `Click to change color: ${newColor}`;
    }
  });
}

// Export utility function
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
