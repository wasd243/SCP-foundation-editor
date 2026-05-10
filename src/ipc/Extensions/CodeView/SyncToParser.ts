import { invoke } from "@tauri-apps/api/core";

type CodeViewMessage = {
  type: "code-view-content-changed";
  payload: string;
};

type ParseOutput = {
  html: string;
  ast_json: string;
};

export function SyncToParser() {
  window.addEventListener("message", async (event: MessageEvent<CodeViewMessage>) => {
    if (event.data?.type !== "code-view-content-changed") return;

    const output = await invoke<ParseOutput>("parse_wikidot", { sourceText: event.data.payload });

    console.log("[UI] Received\n")
    console.log(event.data.payload);

    window.dispatchEvent(new CustomEvent("code-view-parser-html", {
      detail: output.html,
    }));
  });
}
