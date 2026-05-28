import { createApp } from "vue";
import App from "./App.vue";
import "vue3-colorpicker/style.css";
import { connectIpc } from "./ipc/ipc";

import "./styles/global.css"
import "./styles/varibles.css";
import "./styles/ribbon.css";
import "./styles/toolbar/basic.css";
import "./styles/toolbar/size.css";
import "./styles/toolbar/color.css";
import "./styles/toolbar/list.css";
import "./styles/toolbar/align.css";
import "./styles/toolbar/components/cards.css";
import "./styles/toolbar/components/actions.css";
// Use SCSS as the editor default theme
// `immutable.scss` is the default theme as ProseMirror theme.
// Could not be muted by usertheme
import "./styles/theme/immutable.scss";
// user theme can mute `default.scss`
import "./styles/theme/default.scss";
import "./styles/contextmenu/menudefault.css";
import "./styles/contextmenu/menutable.css";
import "./styles/toolbar/url.css";
import "./styles/toolbar/insertion.css";

connectIpc();
createApp(App).mount("#app");
