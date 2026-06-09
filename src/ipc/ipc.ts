import { CodeView } from "./Extensions/CodeView";
import { CodeExport } from "./Extensions/CodeExport";

export async function connectIpc() {
  CodeView();
  await CodeExport();
}
