export type FormatCommand = "bold" | "italic" | "underline" | "strike";

export async function runFormatCommand(command: FormatCommand): Promise<void> {
    console.log("[format command]", command);

    // 以后这里接 TipTap：
    // editor.chain().focus().toggleBold().run()

    // 或者接 Tauri/Rust：
    // await invoke("run_format_command", { command });
}