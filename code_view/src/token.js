import { ExternalTokenizer } from "@lezer/lr"
import * as Terms from "./parser.terms.js"

// 1. 定义 Term 映射，方便维护
const { 
  StrongText, 
  EmText, 
  SupText, 
  SubText, 
  Original, 
  UnderlineText, 
  StrikeText, 
  Hr 
} = Terms

// 2. 字符常量定义
const char = {
  asterisk: 42,   // *
  slash: 47,      // /
  caret: 94,      // ^
  comma: 44,      // ,
  at: 64,         // @
  underscore: 95, // _
  dash: 45,       // -
  newline: 10,    // \n
  return: 13      // \r
};

/**
 * 通用的双符号包裹匹配器 (e.g., **bold**, //italic//)
 * @param {input} input Lezer Input stream
 * @param {number} code 字符代码 (如 char.asterisk)
 * @param {number} termId 对应的 Term ID
 * @param {boolean} checkThird 检查第三个字符是否相同（防止 *** 或 /// 误触）
 */
function scanPair(input, code, termId, checkThird = false) {
  if (input.next == code && input.peek(1) == code) {
    // 如果设置了 checkThird，则要求第三个字符不能还是同一个符号
    if (checkThird && input.peek(2) == code) return false;

    let offset = 2;
    let hasContent = false;

    while (true) {
      let curr = input.peek(offset);
      
      // 遇到行尾或文档尾，匹配失败
      if (curr == -1 || curr == char.newline || curr == char.return) break;

      // 寻找闭合符号
      if (curr == code && input.peek(offset + 1) == code) {
        if (hasContent) {
          // 成功找到闭合且中间有内容
          for (let i = 0; i < offset + 2; i++) input.advance();
          input.acceptToken(termId);
          return true;
        }
        break; // 空的内容 (如 ****) 不视为合法标记
      }
      
      hasContent = true;
      offset++;
    }
  }
  return false;
}

export const inlineTokenizer = new ExternalTokenizer((input) => {
  const next = input.next;

  // --- 1. 处理 StrongText (**) ---
  if (next == char.asterisk) {
    if (scanPair(input, char.asterisk, StrongText, true)) return;
  }

  // --- 2. 处理 EmText (//) ---
  if (next == char.slash) {
    if (scanPair(input, char.slash, EmText, true)) return;
  }

  // --- 3. 处理 SupText (^^) ---
  if (next == char.caret) {
    if (scanPair(input, char.caret, SupText)) return;
  }

  // --- 4. 处理 SubText (,,) ---
  if (next == char.comma) {
    if (scanPair(input, char.comma, SubText)) return;
  }

  // --- 5. 处理 Original (@@) ---
  if (next == char.at) {
    if (scanPair(input, char.at, Original)) return;
  }

  // --- 6. 处理 UnderlineText (__) ---
  if (next == char.underscore) {
    if (scanPair(input, char.underscore, UnderlineText)) return;
  }

  // --- 7. 处理连字号 (Hr & StrikeText) ---
  if (next == char.dash) {
    let count = 0;
    while (input.peek(count) == char.dash) count++;

    // A: Hr (4个或更多 -)
    if (count >= 4) {
      for (let i = 0; i < count; i++) input.advance();
      input.acceptToken(Hr);
      return;
    }

    // B: StrikeText (--内容--)
    if (count == 2) {
      // 这里不使用 scanPair 是因为需要特殊处理排除 --- 的情况
      let offset = 2;
      let hasContent = false;
      while (true) {
        let curr = input.peek(offset);
        if (curr == -1 || curr == char.newline || curr == char.return) break;
        if (curr == char.dash && input.peek(offset + 1) == char.dash) {
          // 确保结尾不是 --- 
          if (input.peek(offset + 2) != char.dash) {
            if (hasContent) {
              for (let i = 0; i < offset + 2; i++) input.advance();
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