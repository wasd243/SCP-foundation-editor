# wiki_css module

### Why this module exists

At first, I wanted to use the `lightningcss` library to minify CSS.
But it's not working well with the sanitizing/nomalization process.
So I decided to move CSS adapter into frontend code, the TypeScript has a good environment on CSS editng rather than parsing.

I decided to use `PostCSS` library to minify CSS in frontend, and leave this module to parse `@import` rules.

---

### How to use

Directly use public function `preprocess(ftml)` to parse the `.ftml` wiki theme file into plain CSS.
Because of some legacy/Wikidot problems, it's maybe left some undefined variables in the CSS, ignore them.

---

### Where's other module depends on this one

Currently, only `w_parser` module depends on this one.
