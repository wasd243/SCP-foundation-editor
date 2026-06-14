## In `btnToolBar`

This folder contains ALL toolbar components.

| Component                 | Description                                                                                                                                                         |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `BtnToolBar`              | The main component folder.                                                                                                                                          |
| `btnAlign`                | All align button like left, right, but except justify                                                                                                               |
| `btnBasic`                | All basic button shown in `HOME` ribbon page: bold, italic, sub, sup, underline, hr, quote, strikethrough table, collapsible. _(Why I put collapsible in `Basic`?)_ |
| `btnColor`                | Only one `btnColorPicker.ts`, I put it in a folder because that's looks good                                                                                        |
| `btnList`                 | All list buttons: `btnOrderedList.ts` and `btnUnorderedList.ts`                                                                                                     |
| `btnSize`                 | All size buttons like larger or smaller, also include size lists _(Size lists are not in `btnList\`)_                                                               |
| `btnActions`              | This folder is not in `btnFormats\` because those 2 files are only connect with `redo` and `undo`                                                                   |
| `btnInsertion`            | This folder contains all insertion buttons like `[[image]]` and all `[[include]]` (NO THEMES)                                                                       |
| `btnNonIncludeComponents` | This folder contains all non include components such as `[[tabview]]` `[[footnote]]` `[[code]]` `[[note]]`                                                          |

### All files in the folder are connected to the same name file

Actually, those files are just `connections` to the `.vue` files.

So it would be better to change one file, rather than all files in folders.
