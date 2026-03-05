function updateTerminalStyle() {
    // Map DIV classes from Header to Box for Live Preview
    var divBoxes = document.querySelectorAll('.div-box');
    divBoxes.forEach(function (box) {
        var header = box.querySelector('.div-header');
        if (header) {
            var text = header.textContent || ""; // Use textContent for robustness
            // STRICT PARSING: Only check the first line (same line as DIV:...)
            var firstLine = text.split('\n')[0];
            // Ensure we are matching `class="..."` specifically
            var match = firstLine.match(/class="([^"]+)"/);
            if (match) {
                var clsList = match[1].split(' ');
                clsList.forEach(function (c) { if (c) box.classList.add(c); });
            }
        }
    });

    var hasTerminal = false;
    var hasTerminal001 = false;
    var cssModules = document.querySelectorAll('.css-box .css-content');
    var allCss = "";

    cssModules.forEach(function (mod) {
        var text = mod.textContent; // FIX: Use textContent to read hidden/collapsed CSS
        allCss += text + "\n";
        if (text.indexOf('.danke') !== -1 && text.indexOf('.agent') !== -1) {
            hasTerminal = true;
        }
        // Revert to looser detection to ensure it catches existing modules
        if (text.indexOf('div.terminal') !== -1 || text.indexOf('.terminal') !== -1) {
            hasTerminal001 = true;
        }
    });

    // PERMANENT RENDERING FIX:
    // If Terminal #001 CSS exists, FIND all div-boxes that look like Terminal #001 (contain scanline)
    // and FORCE the 'terminal' class on them.
    if (hasTerminal001) {
        divBoxes.forEach(function (box) {
            // Check for scanline child (Unique feature of Terminal #001)
            // Scanline is a nested div-box with "scanline" in its header
            var headers = box.querySelectorAll('.div-header');
            var isTerminal = false;
            for (var i = 0; i < headers.length; i++) {
                // Use textContent here as well
                if (headers[i].textContent.indexOf('scanline') !== -1) {
                    isTerminal = true;
                    break;
                }
            }

            if (isTerminal) {
                if (!box.classList.contains('terminal')) {
                    box.classList.add('terminal');
                }
            }
        });
    }

    var styleId = 'dynamic-terminal-style';
    var style = document.getElementById(styleId);

    // Build extra CSS
    var extraInfo = "";

    if (hasTerminal) {
        extraInfo += `
                        /* Force Terminal Style for all DIV modules in Editor View */
                        .div-box {
                            background-color: #000000 !important;
                            border: 2px solid #55AA55 !important;
                            color: #77CC77 !important;
                            font-family: 'Courier New', monospace !important;
                        }
                        .div-header {
                            background-color: #55AA55 !important;
                            color: #002200 !important;
                            border-bottom: 1px solid #002200 !important;
                            font-weight: bold;
                        }
                        .div-content {
                            background-color: #000000 !important;
                            color: #77CC77 !important;
                        }
                        `;
    }

    if (hasTerminal001) {
        extraInfo += `
                         /* Fix for Terminal #001 Nested Divs */
                         .div-box.terminal .div-box {
                             background-color: #000000 !important;
                             border: 1px dashed #333 !important; 
                             box-shadow: none !important; 
                         }
                         /* Nested Content Black */
                         .div-box.terminal .div-box .div-content {
                             background-color: #000000 !important;
                             color: #77CC77 !important;
                         }
                         /* Nested Headers - HIDE for Clean Preview */
                         .div-box.terminal .div-box .div-header {
                             display: none !important;
                         }

                         /* FORCE ALL DESCENDANTS BLACK BACKGROUND (except special text) */
                         .div-box.terminal * {
                             background-color: transparent; /* Default to transp so parent black shows, avoids white patches */
                         }
                         .div-box.terminal .div-content {
                             background-color: #000000 !important; /* Ensure main container is black */
                         }
                         .div-box.terminal blockquote,
                         .div-box.terminal blockquote * {
                             background-color: #000000 !important;
                             color: #77CC77 !important;
                             border-color: #77CC77 !important; /* Ensure border color matches */
                         }
                         .div-box.terminal blockquote {
                             border: 3px double #77CC77 !important;
                         }

                         /* EXCEPTION: Scanline - HIDDEN in Editor View */
                         .div-box.terminal .div-box.scanline {
                             display: none !important;
                         }

                         /* Fix for OUTER Terminal .div-box */
                         .div-box.terminal {
                             background-color: #000000 !important;
                             border: 3px solid #BBBBBB !important;
                             border-radius: 16px !important;
                             box-shadow: inset 0 0 10em 1em rgba(0,0,0,0.5) !important;
                         }
                         /* Outer Content Transparent */
                         .div-box.terminal > .div-content {
                             background-color: transparent !important;
                             color: #77CC77 !important;
                             padding: 2px !important;
                         }
                         /* Outer Header - HIDE for Clean Preview */
                         .div-box.terminal > .div-header {
                              display: none !important;
                         }
                         `;
    }

    var editorText = document.getElementById('editor-root').innerText;
    if (allCss.indexOf('black-highlighter-theme') !== -1 || editorText.indexOf('black-highlighter-theme') !== -1) {
        document.getElementById('editor-root').classList.add('bhl-theme');
    } else if (allCss.indexOf('shivering') !== -1 || editorText.indexOf('shivering') !== -1) {
        document.getElementById('editor-root').classList.add('shivering-theme');
    } else if (allCss.indexOf('basalt') !== -1 || editorText.indexOf('basalt') !== -1) {
        document.getElementById('editor-root').classList.add('basalt-theme');
    } else {
        document.body.classList.remove('bhl-theme');
        document.getElementById('editor-root').classList.remove('shivering-theme');
    }

    if (allCss.trim()) {
        if (!style) {
            style = document.createElement('style');
            style.id = styleId;
            document.head.appendChild(style);
        }
        style.textContent = allCss + extraInfo;
    } else if (style) {
        style.textContent = "";
    }
}