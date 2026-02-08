//import {markedHighlight} from "marked-highlight";

marked.use(markedHighlight({
    langPrefix: 'language-',
    highlight(code, lang) {

        const highlighter = new Sunlight.Highlighter();

        //first argument is the text to highlight, second is the language id
        const context = highlighter.highlight(code, lang);
        const nodes = context.getNodes(); //array of DOM nodes

        //the following will convert it to an HTML string
        const dummyElement = document.createElement("div");
        for (let i = 0; i < nodes.length; i++) {
            dummyElement.appendChild(nodes[i]);
        }

        const rawHtml = dummyElement.innerHTML + '<br>';

        return rawHtml
    }
}));

/******************************************************************
 * Collapse code blocks longer than this many lines
 ******************************************************************/
const CODE_LINE_THRESHOLD = 10;

/******************************************************************
 * Helpers
 ******************************************************************/
function toPlainString(value) {
  // turns undefined / null into '', objects into '[object Object]'
  // which is still a string we can safely .split('\n') on
  return (typeof value === 'string') ? value : String(value ?? '');
}

function countLines(str) {
  return str.replace(/\n$/, '').split('\n').length;  // ignore trailing \n
}

/******************************************************************
 * 1 · Grab the default renderer (already wired to marked-highlight)
 ******************************************************************/
const stockRenderer = new marked.Renderer();

/******************************************************************
 * 2 · Our thin wrapper around its .code() method
 ******************************************************************/
const wrapperRenderer = {
  code(rawCode, lang, escaped) {
    // marked v14+ passes a token object {text, lang, escaped} as first arg
    const text = (typeof rawCode === 'object') ? rawCode.text : rawCode;
    const plain = toPlainString(text);
    const lines = countLines(plain);

    // Let the original renderer build the highlighted HTML
    const html = stockRenderer.code(rawCode, lang, escaped);

    // Long snippet → wrap in <details> so it starts collapsed
    if (lines > CODE_LINE_THRESHOLD) {
      return `
<details class="code-collapse">
  <summary>Show code (${lines} lines)...</summary>
  ${html}
</details>`;
    }
    return html;
  }

};

/******************************************************************
 * 3 · Tell marked to use our wrapper
 ******************************************************************/
marked.use({ renderer: wrapperRenderer });




function parse_markdown(str) {
  // 1️⃣ Turn Markdown into HTML (already highlighted etc.)
  str = marked.parse(str);

  // 2️⃣ Make ordered lists look right in Tailwind
  str = str.replace('<ol>', '<ol class="list-decimal">');

  // 3️⃣ PATCH: add new-tab behaviour + colour class to every link
  //    – works no matter what Marked generated for the <a>
  str = str.replace(
    /<a\s/gi,
    '<a target="_blank" rel="noopener noreferrer" class="chat-link" '
  );

  return str;
}

// Endpoint for websocket:
const endpoint = "ws://localhost:" + WS_PORT + "/chat";

// Default subtitle:
const default_subtitle = 'Ask a question, ask for a widget, ask to process images, or control the napari viewer!<br><a href="https://github.com/royerlab/napari-chatgpt/wiki/Tips&Tricks" class="chat-link" target="_blank" rel="noopener noreferrer">How to Prompt Omega - Tips &amp; Tricks</a>';

/******************************************************************
 * WebSocket connection with reconnection logic
 ******************************************************************/
let ws = null;
let reconnectDelay = 1000;          // start at 1 s, doubles on each failure
const MAX_RECONNECT_DELAY = 30000;  // cap at 30 s
let hasConnected = false;           // true after the first successful open

function connect() {
    ws = new WebSocket(endpoint);

    ws.onopen = function () {
        hasConnected = true;
        reconnectDelay = 1000;  // reset backoff on successful connect
        // Remove any connect/disconnect banner
        const banner = document.getElementById('disconnect-banner');
        if (banner) banner.remove();
    };

    ws.onclose = function () {
        showDisconnectBanner();
        scheduleReconnect();
    };

    ws.onerror = function () {
        // onclose will fire after onerror, so reconnection is handled there
    };

    ws.onmessage = onMessage;
}

function showDisconnectBanner() {
    if (document.getElementById('disconnect-banner')) return;
    const messages = document.getElementById('messages');
    const banner = document.createElement('div');
    banner.id = 'disconnect-banner';
    banner.className = 'disconnect-banner';
    banner.textContent = hasConnected
        ? 'Disconnected from server. Reconnecting\u2026'
        : 'Connecting to server\u2026';
    messages.appendChild(banner);
    messages.scrollTop = messages.scrollHeight;

    // Re-enable Send button so the user isn't stuck
    const button = document.getElementById('send');
    button.innerHTML = "Send";
    button.disabled = false;

    const header = document.getElementById('header');
    header.innerHTML = default_subtitle;
    header.classList.remove('thinking');
}

function scheduleReconnect() {
    setTimeout(function () {
        reconnectDelay = Math.min(reconnectDelay * 2, MAX_RECONNECT_DELAY);
        connect();
    }, reconnectDelay);
}

// Receive message from server and process it:
function onMessage(event) {

    // Message list element:
    const messages = document.getElementById('messages');

    // JSON parsing of message data:
    const data = JSON.parse(event.data);

    // Log event on the console for debugging:
    console.log("__________________________________________________________________");
    console.log("data.sender =" + data.sender + '\n');
    console.log("data.type   =" + data.type + '\n');
    console.log("data.message=" + data.message + '\n');

    // Message received from agent:
    if (data.sender === "agent") {
        // start message:
        if (data.type === "start") {
            // Set subtitle:
            const header = document.getElementById('header');
            header.innerHTML = "Thinking... please wait!";
            header.classList.add('thinking');

        }
        // agent is thinking:
        else if (data.type === "thinking") {
            // Set subtitle:
            const header = document.getElementById('header');
            header.innerHTML = 'Thinking...';
            header.classList.add('thinking');
        }
        // tool start:
        else if (data.type === "tool_start") {

            // Set subtitle:
            const header = document.getElementById('header');
            header.innerHTML = "Using a tool... please wait!";
            header.classList.add('thinking');

            // Create a collapsible container for tool output:
            const div = document.createElement('div');
            div.className = 'action-message';

            const details = document.createElement('details');
            details.className = 'tool-collapse';

            const summary = document.createElement('summary');
            summary.innerHTML = "<strong>" + "Omega: " + "</strong>" + parse_markdown(data.message);
            details.appendChild(summary);

            // Body element for tool activity and results:
            const body = document.createElement('div');
            body.className = 'tool-collapse-body';
            details.appendChild(body);

            div.appendChild(details);
            messages.appendChild(div);

        }
        // Tool activity:
        else if (data.type === "tool_activity") {
            // Find the tool collapse body in the last message:
            const last = messages.lastChild;
            const body = last && last.querySelector
                       ? last.querySelector('.tool-collapse-body')
                       : null;
            if (!body) return;

            // Parse markdown and render as HTML:
            body.innerHTML += parse_markdown(data.message)

        }
        // Tool result:
        else if (data.type === "tool_result") {
            // Find the tool collapse body in the last message:
            const last = messages.lastChild;
            const body = last && last.querySelector
                       ? last.querySelector('.tool-collapse-body')
                       : null;
            if (!body) return;

            // Parse markdown and render as HTML:
            body.innerHTML += "<br>" + parse_markdown(data.message)

            // Auto-expand tool details if the result indicates an error:
            if (/error|failed|exception/i.test(data.message)) {
                const details = last.querySelector('details.tool-collapse');
                if (details) details.open = true;
            }

        }
        // end message, this is sent once the agent has a final response:
        else if (data.type === "final") {
            // Create a new message entry:
            const div = document.createElement('div');
            div.className = 'server-message';
            const p = document.createElement('p');

            // Add message to message list:
            div.appendChild(p);
            messages.appendChild(div);

            // Set background color:
            p.parentElement.className = 'server-message';

            // Parse markdown and render as HTML:
            p.innerHTML = "<strong>" + "Omega: " + "</strong>" + parse_markdown(data.message)

            // Reset subtitle:
            const header = document.getElementById('header');
            header.innerHTML = default_subtitle;
            header.classList.remove('thinking');

            // Reset button text and state:
            const button = document.getElementById('send');
            button.innerHTML = "Send";
            button.disabled = false;
        }
        // Error:
        else if (data.type === "error") {
            // Reset subtitle:
            const header = document.getElementById('header');
            header.innerHTML = default_subtitle;
            header.classList.remove('thinking');

            // Reset button text and state:
            const button = document.getElementById('send');
            button.innerHTML = "Send";
            button.disabled = false;

            // Auto-expand the preceding tool-collapse so the user
            // can see what code/action caused the error:
            const prev = messages.lastChild;
            if (prev) {
                const details = prev.querySelector
                              ? prev.querySelector('details.tool-collapse')
                              : null;
                if (details) details.open = true;
            }

            // Create a new message entry:
            const div = document.createElement('div');
            div.className = 'server-message';
            const p = document.createElement('p');

            // Add message to message list:
            div.appendChild(p);
            messages.appendChild(div);

            // Display error message:
            p.innerHTML = "<strong>" + "Omega: " + "</strong>" + parse_markdown(data.message)

            // Set background color:
            p.parentElement.className = 'error-message';
        }
    }
    // Message received from user:
    else if (data.sender === "user") {
        // Create new message entry:
        const div = document.createElement('div');
        div.className = 'client-message';
        const p = document.createElement('p');

        // Set default (empty) message:
        p.innerHTML = "<strong>" + "You: " + "</strong>";
        p.innerHTML += parse_markdown(data.message);

        // Add message to message list:
        div.appendChild(p);
        messages.appendChild(div);
    }
    // Scroll to the bottom of the chat
    messages.scrollTop = messages.scrollHeight;
}

// Start the WebSocket connection:
connect();


// Send message to server
function sendMessage(event) {
    event.preventDefault();
    const message = document.getElementById('messageText').value;
    if (message === "") {
        return;
    }
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        return;
    }
    ws.send(message);
    document.getElementById('messageText').value = "";

    // Turn the button into a loading button
    const button = document.getElementById('send');
    button.innerHTML = "Loading...";
    button.disabled = true;
}
