import {
    Table,
    TableCell,
    TableHeader,
    TableRow,
} from "@tiptap/extension-table";

export const TableExtensions = [
    Table.configure({
        resizable: true,
    }),
    TableRow,
    TableHeader,
    TableCell,
];
