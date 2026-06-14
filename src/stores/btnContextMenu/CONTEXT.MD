## In `btnContextMenu\`

This folder contains the context menu for the buttons, which is a right-click menu.

There are some different types of architecture:

### `table\` like

This is the most common architecture. The main content is in `name.ts`. _(like `table.ts`)_
The files in folder are only connected to the `.vue` files buttons.

### `TabView\` like

This architecture is used in `tabView.ts`.
The files in the folder contain the context menu code for the tab view.
The `.vue` files buttons are all connected to the `TabView.ts`.
