import type { Editor } from "@tiptap/core";
import type { ResolvedPos } from "@tiptap/pm/model";

export type ContextMenuFlags = {
  showTabView: boolean;
  showTable: boolean;
};

const TAB_VIEW_NODE_NAMES = new Set([
  "tabView",
  "tabViewButtonList",
  "tabViewButton",
  "tabViewPanelList",
  "tabViewPanel",
]);

const TABLE_NODE_NAMES = new Set([
  "table",
  "tableRow",
  "tableHeader",
  "tableCell",
]);

function flagsFromResolvedPos($pos: ResolvedPos): ContextMenuFlags {
  let showTabView = false;
  let showTable = false;

  for (let depth = $pos.depth; depth > 0; depth -= 1) {
    const nodeName = $pos.node(depth).type.name;

    if (TAB_VIEW_NODE_NAMES.has(nodeName)) {
      showTabView = true;
    }

    if (TABLE_NODE_NAMES.has(nodeName)) {
      showTable = true;
    }
  }

  return { showTabView, showTable };
}

function flagsFromDomTarget(target: EventTarget | null | undefined): ContextMenuFlags {
  if (!(target instanceof Element)) {
    return { showTabView: false, showTable: false };
  }

  return {
    showTabView: Boolean(target.closest("wj-tabs")),
    showTable: Boolean(target.closest("table")),
  };
}
function mergeFlags(a: ContextMenuFlags, b: ContextMenuFlags): ContextMenuFlags {
  return {
    showTabView: a.showTabView || b.showTabView,
    showTable: a.showTable || b.showTable,
  };
}

export function getContextMenuFlags(
  editor: Editor,
  clickPos?: number | null,
  eventTarget?: EventTarget | null,
): ContextMenuFlags {
  const positions: ResolvedPos[] = [editor.state.selection.$from, editor.state.selection.$to];

  if (clickPos !== null && clickPos !== undefined && Number.isInteger(clickPos)) {
    const docSize = editor.state.doc.content.size;

    if (clickPos >= 0 && clickPos <= docSize) {
      positions.push(editor.state.doc.resolve(clickPos));
    }
  }

  let flags: ContextMenuFlags = flagsFromDomTarget(eventTarget);

  for (const $pos of positions) {
    flags = mergeFlags(flags, flagsFromResolvedPos($pos));
  }

  return mergeFlags(flags, {
    showTabView: editor.isActive("tabView") || editor.isActive("tabViewPanel"),
    showTable: editor.isActive("table"),
  });
}