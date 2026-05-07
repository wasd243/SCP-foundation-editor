项目骨架说明（中文）

结构概览：
- frontend/: Vue 3 + TypeScript + TipTap 编辑器前端
- src-tauri/: Tauri / Rust 后端，暴露 parse/render/serialize 命令

快速开始（开发）：
1. 前端：
   cd frontend
   npm install
   npm run dev

2. Tauri（开发）：
   在项目根或 frontend 中运行 tauri dev（取决于你的 npm 脚本）

注意事项：
- 目前后端命令为示例 stub，需要在 src-tauri/src/main.rs 中接入仓内的 ftml crate（已有 ftml 目录）。
- 建议先在 Rust 端实现 FTML AST -> JSON 的导出，然后在前端实现 TipTap doc ⇄ FTML AST 的映射器。
