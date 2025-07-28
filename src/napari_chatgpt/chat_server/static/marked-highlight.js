/**
 * Creates a configuration object for integrating syntax highlighting with a markdown parser.
 *
 * Accepts either a highlight function or an options object containing a highlight function, and returns an object with methods for processing and rendering code blocks with syntax highlighting. Supports both synchronous and asynchronous highlight functions, configurable language class prefix, and safe HTML escaping for code output.
 *
 * @param {Function|Object} options - A highlight function or an options object with a `highlight` function, optional `async` boolean, and optional `langPrefix` string.
 * @return {Object} An object with properties and methods for token walking and code rendering, suitable for use with a markdown parser.
 * @throws {Error} If a valid highlight function is not provided, or if an asynchronous highlight function is used without enabling async mode.
 */
function markedHighlight(options) {
    if (typeof options === 'function') {
        options = {
            highlight: options,
        };
    }

    if (!options || typeof options.highlight !== 'function') {
        throw new Error('Must provide highlight function');
    }

    if (typeof options.langPrefix !== 'string') {
        options.langPrefix = 'language-';
    }

    return {
        async: !!options.async,
        walkTokens(token) {
            if (token.type !== 'code') {
                return;
            }

            const lang = getLang(token.lang);

            if (options.async) {
                return Promise.resolve(options.highlight(token.text, lang, token.lang || '')).then(updateToken(token));
            }

            const code = options.highlight(token.text, lang, token.lang || '');
            if (code instanceof Promise) {
                throw new Error('markedHighlight is not set to async but the highlight function is async. Set the async option to true on markedHighlight to await the async highlight function.');
            }
            updateToken(token)(code);
        },
        useNewRenderer: true,
        renderer: {
            code(code, infoString, escaped) {
                // istanbul ignore next
                if (typeof code === 'object') {
                    escaped = code.escaped;
                    infoString = code.lang;
                    code = code.text;
                }

                const lang = getLang(infoString);
                const classAttr = lang
                    ? ` class="${options.langPrefix}${escape(lang)}"`
                    : '';
                code = code.replace(/\n$/, '');
                return `<pre><code${classAttr}>${escaped ? code : escape(code, true)}\n</code></pre>`;
            },
        },
    };
}

/**
 * Extracts the first non-whitespace substring from a language string.
 * @param {string} lang - The language string, which may contain additional whitespace or metadata.
 * @return {string} The extracted language identifier, or an empty string if none is found.
 */
function getLang(lang) {
    return (lang || '').match(/\S*/)[0];
}

/**
 * Returns a function that updates a token's text and marks it as escaped if the new code differs from the original.
 * @param {object} token - The token object to update, with `text` and `escaped` properties.
 * @return {function(string): void} A function that takes a code string and updates the token if necessary.
 */
function updateToken(token) {
    return (code) => {
        if (typeof code === 'string' && code !== token.text) {
            token.escaped = true;
            token.text = code;
        }
    };
}

// copied from marked helpers
const escapeTest = /[&<>"']/;
const escapeReplace = new RegExp(escapeTest.source, 'g');
const escapeTestNoEncode = /[<>"']|&(?!(#\d{1,7}|#[Xx][a-fA-F0-9]{1,6}|\w+);)/;
const escapeReplaceNoEncode = new RegExp(escapeTestNoEncode.source, 'g');
const escapeReplacements = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
};
const getEscapeReplacement = (ch) => escapeReplacements[ch];

/**
 * Escapes special HTML characters in a string to prevent HTML injection.
 * @param {string} html - The string to escape.
 * @param {boolean} encode - If true, escapes all occurrences of `&`, `<`, `>`, `"`, and `'`. If false, escapes only unsafe characters not already part of an HTML entity.
 * @return {string} The escaped string, or the original string if no escaping is needed.
 */
function escape(html, encode) {
    if (encode) {
        if (escapeTest.test(html)) {
            return html.replace(escapeReplace, getEscapeReplacement);
        }
    } else {
        if (escapeTestNoEncode.test(html)) {
            return html.replace(escapeReplaceNoEncode, getEscapeReplacement);
        }
    }

    return html;
}