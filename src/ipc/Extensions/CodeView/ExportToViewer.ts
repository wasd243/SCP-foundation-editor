import { SyncJSONToExporter } from "../CodeExport/getJSON";

let _codeViewIframe: HTMLIFrameElement | null = null;

type CodeViewWindow = Window & {
    setCodeViewContent?: (content: string) => boolean;
};

export function setExportIframe(iframe: HTMLIFrameElement | null) {
    _codeViewIframe = iframe;
}

function wait(ms: number) {
    return new Promise<void>((resolve) => window.setTimeout(resolve, ms));
}

async function sendContentToCodeView(content: string) {
    const iframe = _codeViewIframe;
    const win = iframe?.contentWindow as CodeViewWindow | null | undefined;
    if (!win) {
        console.warn("[ExportToViewer] iframe is not ready yet");
        return;
    }

    for (let attempt = 0; attempt < 20; attempt += 1) {
        try {
            if (
                typeof win.setCodeViewContent === "function" &&
                win.setCodeViewContent(content)
            ) {
                console.log(
                    "[ExportToViewer] content applied through iframe API",
                );
                return;
            }
        } catch (error) {
            console.warn(
                "[ExportToViewer] iframe API was not accessible. Falling back to postMessage.",
                error,
            );
            break;
        }

        await wait(50);
    }

    console.warn(
        "[ExportToViewer] iframe API was not ready. Falling back to postMessage.",
    );
    win.postMessage(
        {
            type: "export-to-viewer-content",
            payload: content,
        },
        "*",
    );
}

export async function exportToViewer() {
    try {
        const sourceText = await SyncJSONToExporter();
        if (sourceText === null) {
            throw new Error("Editor is not ready yet.");
        }

        await sendContentToCodeView(sourceText);
    } catch (error) {
        console.error("[ExportToViewer] failed to export ftml", error);
        throw error;
    }
}
