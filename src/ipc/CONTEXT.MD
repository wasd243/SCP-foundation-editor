## In `ipc\`
This folder contains the IPC code, which is used to communicate between Rust and TS.

```ts
import {invoke} from "@tauri-apps/api/core";

await invoke = ("ipc_name"); 
```

Use `invoke` to call the tauri IPC.

---

## In `ipc\Extensions\CodeView\htmlAdapter\Components\`
This folder contains the HTML adapter which to adapt the HTML output from `ftml` parser to TipTap format.
