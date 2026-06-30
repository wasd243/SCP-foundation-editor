## In `Topbar\`

This folder contains ribbon pages and ribbon button.

All ribbon pages file will be imported to `(RibbonName).vue` files.

All `(RibbonName).vue` files will be imported to `Ribbon.vue` file.

`Ribbon.vue` will be imported to `Topbar.vue` file.

### Ribbon Pages

| Ribbon | Page                    | Ribbon Button       |
| ------ | ----------------------- | ------------------- |
| Home   | `Ribbon/HomePage.vue`   | `Topbar/Home.vue`   |
| Insert | `Ribbon/InsertPage.vue` | `Topbar/Insert.vue` |

Settings now live in a modal window (`src/components/settings/Settings.vue`),
opened from the gear button in the Actions bar — they are no longer a ribbon page.
