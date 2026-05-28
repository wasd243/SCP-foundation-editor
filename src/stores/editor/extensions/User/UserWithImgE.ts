import { createUserNodeExtension } from "./createUserNodeExtension.ts";

export function insertUserWithImg() {}

export const UserWithImgExtension = createUserNodeExtension({
    name: "userWithImg",
    className: "wj-user-with-img",
});
