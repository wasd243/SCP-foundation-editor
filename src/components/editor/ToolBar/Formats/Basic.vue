<script setup lang="ts">
import Bold from "./Basic/Bold.vue";
import Italic from "./Basic/Italic.vue";
import Underline from "./Basic/Underline.vue";
import Strikethrough from "./Basic/Strikethrough.vue";
import Sub from "./Basic/Sub.vue";
import Sup from "./Basic/Sup.vue";
import Quote from "./Basic/Quote.vue";
import { toggleBoldEditor } from "../../../../stores/btnToolBar/btnFormats/btnBasic/btnBold.ts";
import { toggleItalicEditor } from "../../../../stores/btnToolBar/btnFormats/btnBasic/btnItalic.ts";
import { toggleUnderlineEditor } from "../../../../stores/btnToolBar/btnFormats/btnBasic/btnUnderline.ts";
import { toggleStrikethroughEditor } from "../../../../stores/btnToolBar/btnFormats/btnBasic/btnStrikethrough.ts";
import { toggleSubscriptEditor } from "../../../../stores/btnToolBar/btnFormats/btnBasic/btnSub.ts";
import { toggleSuperscriptEditor } from "../../../../stores/btnToolBar/btnFormats/btnBasic/btnSup.ts";
import { toggleQuoteEditor } from "../../../../stores/btnToolBar/btnFormats/btnBasic/btnQuote.ts";
import { insertTableEditor } from "../../../../stores/btnToolBar/btnFormats/btnBasic/btnTable.ts";
import { insertHorizontalRuleEditor } from "../../../../stores/btnToolBar/btnFormats/btnBasic/btnHr.ts";
import Table from "./Basic/Table.vue";
import Hr from "./Basic/Hr.vue";
import Collapsible from "./Basic/Collapsible.vue";

function toggleBold() {
  toggleBoldEditor();
}

function toggleItalic() {
  toggleItalicEditor();
}

function toggleUnderline() {
  toggleUnderlineEditor();
}

function toggleStrikethrough() {
  toggleStrikethroughEditor();
}

function toggleSubscript() {
  toggleSubscriptEditor();
}

function toggleSuperscript() {
  toggleSuperscriptEditor();
}

function toggleQuote() {
  toggleQuoteEditor();
}

function insertTable() {
  insertTableEditor();
}

function insertHorizontalRule() {
  insertHorizontalRuleEditor();
}

function basicIdleInterface() {}

defineExpose({
  basicIdleInterface,
});
</script>

<template>
  <Bold @toggle="toggleBold"/>
  <Italic @toggle="toggleItalic"/>
  <Underline @toggle="toggleUnderline"/>
  <Strikethrough @toggle="toggleStrikethrough"/>
  <Sub @toggle="toggleSubscript"/>
  <Sup @toggle="toggleSuperscript"/>
  <Quote @toggle="toggleQuote"/>
  <Table @insert="insertTable"/>
  <Hr @insert="insertHorizontalRule"/>
  <Collapsible/>
</template>
