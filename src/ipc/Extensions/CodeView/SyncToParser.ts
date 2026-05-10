import { invoke } from "@tauri-apps/api/core";

type CodeViewMessage = {
  type: "code-view-content-changed";
  payload: string;
};

export function SyncToParser() {
  window.addEventListener("message", async (event: MessageEvent<CodeViewMessage>) => {
    if (event.data?.type !== "code-view-content-changed") return;

    await invoke("parse_wikidot", { sourceText: event.data.payload });

    console.log("[UI] Received\n")
    console.log(event.data.payload);
  });
}
