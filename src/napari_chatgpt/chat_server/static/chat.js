//import {markedHighlight} from "marked-highlight";

marked.use(markedHighlight({
    langPrefix: 'language-',
    highlight(code, lang) {

        var highlighter = new Sunlight.Highlighter();

        //first argument is the text to highlight, second is the language id
        var context = highlighter.highlight(code, lang);
        var nodes = context.getNodes(); //array of DOM nodes

        //the following will convert it to an HTML string
        var dummyElement = document.createElement("div");
        for (var i = 0; i < nodes.length; i++) {
            dummyElement.appendChild(nodes[i]);
        }

        var rawHtml = dummyElement.innerHTML + '<br>';

        console.log(rawHtml)

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
    const plain = toPlainString(rawCode);       // ← fix for the crash
    const lines = countLines(plain);

    // Let the original renderer build the highlighted HTML
    const html = stockRenderer.code(rawCode, lang, escaped);

    // Long snippet → wrap in <details> so it starts collapsed
    return `
<details class="code-collapse">
  <summary>Show code...</summary>
  ${html}
</details>`;
  }

};

/******************************************************************
 * 3 · Tell marked to use our wrapper
 ******************************************************************/
marked.use({ renderer: wrapperRenderer });




function escapeHTML(unsafeText) {
    let div = document.createElement('div');
    div.innerText = unsafeText;
    return div.innerHTML;
}

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
var endpoint = "ws://localhost:9000/chat";
var ws = new WebSocket(endpoint);

// Default subtitle:
default_subtitle = " Ask a question, ask for a widget, ask to process images, or control the napari viewer ! ";

// Receive message from server and process it:
ws.onmessage = function (event) {

    // Message list element:
    var messages = document.getElementById('messages');

    // JSON parsingof message data:
    var data = JSON.parse(event.data);

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
            var header = document.getElementById('header');
            header.innerHTML = "Thinking... please wait!";

        }
        // agent is thinking:
        else if (data.type === "thinking") {
            // Set subtitle:
            var header = document.getElementById('header');
            header.innerHTML = 'Thinking...';
        }
        // tool start:
        else if (data.type === "tool_start") {

            // Set subtitle:
            var header = document.getElementById('header');
            header.innerHTML = "Using a tool... please wait!";

            // Create a new message entry:
            var div = document.createElement('div');
            div.className = 'server-message';
            var p = document.createElement('p');

            // Add this new message into message list:
            div.appendChild(p);
            messages.appendChild(div);

            // Current (last) message:
            var p = messages.lastChild.lastChild;

            // Set background color:
            p.parentElement.className = 'action-message';

            // Parse markdown and render as HTML:
            p.innerHTML = "<strong>" + "Omega: " + "</strong>" + marked.parse(data.message)

        }
        // Tool activity:
        else if (data.type === "tool_activity") {
            // Current (last) message:
            var p = messages.lastChild.lastChild;

            // Parse markdown and render as HTML:
            p.innerHTML += "<br>" + parse_markdown(data.message)

        }
        // Tool end:
        else if (data.type === "tool_end") {
            // Current (last) message:
            var p = messages.lastChild.lastChild;

            // Parse markdown and render as HTML:
            p.innerHTML += parse_markdown(data.message)

        }
        // tool result message:
        else if (data.type === "tool_result") {

            // Current (last) message:
            var p = messages.lastChild.lastChild;

            // Parse markdown and render as HTML:
            p.innerHTML += "<br>" + parse_markdown(data.message);
        }
        // end message, this is sent once the agent has a final response:
        else if (data.type === "final") {
            // Create a new message entry:
            var div = document.createElement('div');
            div.className = 'server-message';
            var p = document.createElement('p');

            // Add message to message list:
            div.appendChild(p);
            messages.appendChild(div);

            // Current (last) message:
            var p = messages.lastChild.lastChild;

            // Set background color:
            p.parentElement.className = 'server-message';

            // Parse markdown and render as HTML:
            p.innerHTML = "<strong>" + "Omega: " + "</strong>" + parse_markdown(data.message)

            // Reset subtitle:
            var header = document.getElementById('header');
            header.innerHTML = default_subtitle;

            // Reset button text and state:
            var button = document.getElementById('send');
            button.innerHTML = "Send";
            button.disabled = false;
        }
        // Error:
        else if (data.type === "error") {
            // Reset subtitle:
            var header = document.getElementById('header');
            header.innerHTML = default_subtitle;

            // Reset button text and state:
            var button = document.getElementById('send');
            button.innerHTML = "Send";
            button.disabled = false;

            // Create a new message entry:
            var div = document.createElement('div');
            div.className = 'server-message';
            var p = document.createElement('p');

            // Add message to message list:
            div.appendChild(p);
            messages.appendChild(div);

            // Display error message:
            var p = messages.lastChild.lastChild;
            p.innerHTML = "<strong>" + "Omega: " + "</strong>" + parse_markdown(data.message)

            // Set background color:
            p.parentElement.className = 'error-message';
        }
    }
    // Message received from user:
    else if (data.sender === "user") {
        // Create new message entry:
        var div = document.createElement('div');
        div.className = 'client-message';
        var p = document.createElement('p');

        // Set default (empty) message:
        p.innerHTML = "<strong>" + "You: " + "</strong>";
        p.innerHTML += parse_markdown(data.message);

        // Add message to message list:
        div.appendChild(p);
        messages.appendChild(div);
    }
    // Scroll to the bottom of the chat
    messages.scrollTop = messages.scrollHeight;
};


// Send message to server
function sendMessage(event) {
    event.preventDefault();
    var message = document.getElementById('messageText').value;
    if (message === "") {
        return;
    }
    ws.send(message);
    document.getElementById('messageText').value = "";

    // Turn the button into a loading button
    var button = document.getElementById('send');
    button.innerHTML = "Loading...";
    button.disabled = true;
}


