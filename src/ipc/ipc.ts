import { CodeView } from "./Extensions/CodeView";
import { CodeExport } from "./Extensions/CodeExport";
import { connectCSSAdapter } from "./Themes/cssAdapter.ts";

export async function connectIpc() {
    CodeView();
    await CodeExport();
    await connectCSSAdapter();
}
