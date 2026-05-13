import { invoke } from "@tauri-apps/api/core";
import { scanDOMandReplace } from "./htmlAdapter";

type CodeViewMessage = {
  type: "code-view-content-changed";
  payload: string;
};

type ParseOutput = {
  html: string;
  ast_json: string;
};

let codeViewIframe: HTMLIFrameElement | null = null;

export function setCodeViewIframe(iframe: HTMLIFrameElement | null) {
  codeViewIframe = iframe;
}

export function SyncToParser() {
  window.addEventListener("message", async (event: MessageEvent<CodeViewMessage>) => {
    if (event.source !== codeViewIframe?.contentWindow) return;
    if (event.origin !== window.location.origin) return;
    if (event.data?.type !== "code-view-content-changed") return;

    const output = await invoke<ParseOutput>("parse_wikidot", { sourceText: event.data.payload });

    console.log("[UI] Received\n")
    console.log(event.data.payload);

    window.dispatchEvent(new CustomEvent("code-view-parser-html", {
      // Replace wj formats <div> classes into TipTap formats for render
      detail: scanDOMandReplace(output.html),
    }));
  });
}
