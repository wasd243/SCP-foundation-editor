import { ExternalTokenizer } from "@lezer/lr";
import * as Terms from "./parser.terms.js";

// 1. Define Term mapping for easier maintenance
const {
    StrongText,
    EmText,
    SupText,
    SubText,
    Original,
    UnderlineText,
    StrikeText,
    Hr,
} = Terms;

// 2. Character constants
const char = {
    asterisk: 42, // *
    slash: 47, // /
    caret: 94, // ^
    comma: 44, // ,
    at: 64, // @
    underscore: 95, // _
    dash: 45, // -
    newline: 10, // \n
    return: 13, // \r
};

/**
 * Generic paired-symbol wrapper matcher (e.g., **bold**, //italic//)
 * @param {input} input Lezer Input stream
 * @param {number} code Character code (e.g., char.asterisk)
 * @param {number} termId Matching Term ID
 * @param {boolean} checkThird Check whether the third character matches (to avoid *** or /// false positives)
 */
function scanPair(input, code, termId, checkThird = false) {
    if (input.next == code && input.peek(1) == code) {
        // If checkThird is enabled, the third character must differ
        if (checkThird && input.peek(2) == code) return false;

        let offset = 2;
        let hasContent = false;

        while (true) {
            let curr = input.peek(offset);

            // Stop at line end or document end (no match)
            if (curr == -1 || curr == char.newline || curr == char.return)
                break;

            // Find closing symbols
            if (curr == code && input.peek(offset + 1) == code) {
                if (hasContent) {
                    // Found a valid close with non-empty content
                    for (let i = 0; i < offset + 2; i++) input.advance();
                    input.acceptToken(termId);
                    return true;
                }
                break; // Empty content (e.g., ****) is not valid markup
            }

            hasContent = true;
            offset++;
        }
    }
    return false;
}

export const inlineTokenizer = new ExternalTokenizer((input) => {
    const next = input.next;

    // --- 1. Handle StrongText (**) ---
    if (next == char.asterisk) {
        if (scanPair(input, char.asterisk, StrongText, true)) return;
    }

    // --- 2. Handle EmText (//) ---
    if (next == char.slash) {
        if (scanPair(input, char.slash, EmText, true)) return;
    }

    // --- 3. Handle SupText (^^) ---
    if (next == char.caret) {
        if (scanPair(input, char.caret, SupText)) return;
    }

    // --- 4. Handle SubText (,,) ---
    if (next == char.comma) {
        if (scanPair(input, char.comma, SubText)) return;
    }

    // --- 5. Handle Original (@@) ---
    if (next == char.at) {
        if (scanPair(input, char.at, Original)) return;
    }

    // --- 6. Handle UnderlineText (__) ---
    if (next == char.underscore) {
        if (scanPair(input, char.underscore, UnderlineText)) return;
    }

    // --- 7. Handle dashes (Hr & StrikeText) ---
    if (next == char.dash) {
        let count = 0;
        while (input.peek(count) == char.dash) count++;

        // A: Hr (4 or more dashes)
        if (count >= 4) {
            for (let i = 0; i < count; i++) input.advance();
            input.acceptToken(Hr);
            return;
        }

        // B: StrikeText (--content--)
        if (count == 2) {
            // scanPair isn't used here because --- must be excluded explicitly
            let offset = 2;
            let hasContent = false;
            while (true) {
                let curr = input.peek(offset);
                if (curr == -1 || curr == char.newline || curr == char.return)
                    break;
                if (curr == char.dash && input.peek(offset + 1) == char.dash) {
                    // Ensure closing token is not ---
                    if (input.peek(offset + 2) != char.dash) {
                        if (hasContent) {
                            for (let i = 0; i < offset + 2; i++)
                                input.advance();
                            input.acceptToken(StrikeText);
                            return;
                        }
                    }
                    break;
                }
                hasContent = true;
                offset++;
            }
        }
    }
});
