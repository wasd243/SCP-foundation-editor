import { mergeAttributes, Node } from "@tiptap/core";
import { NodeSelection } from "@tiptap/pm/state";

type UserNodeExtensionOptions = {
    name: string;
    className: string;
};

function getUserText(value: unknown) {
    return typeof value === "string" ? value : "";
}

export function createUserNodeExtension({ name, className }: UserNodeExtensionOptions) {
    return Node.create({
        name,
        priority: 1100,
        group: "inline",
        inline: true,
        atom: true,
        selectable: true,

        addAttributes() {
            return {
                user: {
                    default: "",
                    parseHTML: element => element instanceof HTMLElement ? element.textContent ?? "" : "",
                    renderHTML: () => ({}),
                },
            };
        },

        parseHTML() {
            return [
                {
                    tag: `span.${className}`,
                    priority: 1100,
                    getAttrs: element => element instanceof HTMLElement
                        ? { user: element.textContent ?? "" }
                        : false,
                },
            ];
        },

        renderHTML({ node, HTMLAttributes }) {
            return [
                "span",
                mergeAttributes(HTMLAttributes, { class: className }),
                getUserText(node.attrs.user),
            ];
        },

        addNodeView() {
            return ({ node, getPos, editor }) => {
                let currentNode = node;
                let editing = false;
                const dom = document.createElement("span");
                const input = document.createElement("span");

                function getPosition() {
                    return typeof getPos === "function" ? getPos() : null;
                }

                function syncDom(value: string) {
                    dom.className = className;
                    dom.contentEditable = "false";
                    input.contentEditable = "true";
                    input.spellcheck = false;

                    if (!editing && input.textContent !== value) {
                        input.textContent = value;
                    }

                    if (input.parentElement !== dom) {
                        dom.replaceChildren(input);
                    }
                }

                function placeCaretAtEnd() {
                    const selection = document.getSelection();
                    const range = document.createRange();

                    range.selectNodeContents(input);
                    range.collapse(false);
                    selection?.removeAllRanges();
                    selection?.addRange(range);
                }

                function updateUser(value: string) {
                    const position = getPosition();

                    if (position === null || position === undefined || currentNode.attrs.user === value) return;

                    editor.view.dispatch(
                        editor.view.state.tr.setNodeMarkup(position, undefined, {
                            ...currentNode.attrs,
                            user: value,
                        }, currentNode.marks),
                    );
                }

                function selectNode(event?: Event) {
                    const position = getPosition();

                    event?.preventDefault();
                    event?.stopPropagation();
                    editing = false;
                    updateUser(input.textContent ?? "");

                    if (position === null || position === undefined) return;

                    editor.view.dispatch(
                        editor.view.state.tr.setSelection(NodeSelection.create(editor.view.state.doc, position)),
                    );
                    editor.view.focus();
                }

                function editNode(event?: Event) {
                    event?.preventDefault();
                    event?.stopPropagation();
                    editing = true;
                    input.focus({ preventScroll: true });
                    placeCaretAtEnd();
                }

                function deleteNode() {
                    const position = getPosition();

                    if (position === null || position === undefined) return;

                    editing = false;
                    editor.view.dispatch(
                        editor.view.state.tr.delete(position, position + currentNode.nodeSize),
                    );
                    editor.view.focus();
                }

                function saveAndSelectNode(event?: Event) {
                    event?.preventDefault();
                    event?.stopPropagation();
                    editing = false;
                    updateUser(input.textContent ?? "");
                    selectNode();
                }

                syncDom(getUserText(currentNode.attrs.user));

                dom.addEventListener("mousedown", selectNode);
                dom.addEventListener("dblclick", editNode);
                input.addEventListener("input", () => updateUser(input.textContent ?? ""));
                input.addEventListener("blur", () => {
                    editing = false;
                    updateUser(input.textContent ?? "");
                });
                input.addEventListener("keydown", event => {
                    if (event.key === "Escape" || event.key === "Enter") {
                        saveAndSelectNode(event);
                        return;
                    }

                    if ((event.key === "Backspace" || event.key === "Delete") && !input.textContent) {
                        event.preventDefault();
                        event.stopPropagation();
                        deleteNode();
                    }
                });

                return {
                    dom,
                    stopEvent: event => event.target === input || input.contains(event.target as globalThis.Node),
                    selectNode: () => dom.classList.add("ProseMirror-selectednode"),
                    deselectNode: () => dom.classList.remove("ProseMirror-selectednode"),
                    ignoreMutation: () => true,
                    update: updatedNode => {
                        if (updatedNode.type !== currentNode.type) return false;

                        currentNode = updatedNode;
                        syncDom(getUserText(updatedNode.attrs.user));
                        return true;
                    },
                };
            };
        },
    });
}
