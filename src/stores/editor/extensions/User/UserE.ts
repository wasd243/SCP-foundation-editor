import { createUserNodeExtension } from "./createUserNodeExtension.ts";

export function insertUser() {}

export const UserExtension = createUserNodeExtension({
    name: "user",
    className: "wj-user",
});
