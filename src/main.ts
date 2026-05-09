import { createApp } from "vue";
import App from "./App.vue";
import "vue3-colorpicker/style.css";

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
import "./styles/default.css";
import "./styles/contextmenu/menudefault.css";
import "./styles/contextmenu/menutable.css";

createApp(App).mount("#app");
