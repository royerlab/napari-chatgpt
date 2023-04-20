
// Endpoint for websocket:
var endpoint = "ws://localhost:9000/chat";
var ws = new WebSocket(endpoint);

// Default subtitle:
default_subtitle = "Ask a question, ask for a napari widget, or anything else!";

// Receive message from server and process it:
ws.onmessage = function (event)
{
    // Message list element:
    var messages = document.getElementById('messages');

    // JSON parsingof message data:
    var data = JSON.parse(event.data);

    // Message received from agent:
    if (data.sender === "agent")
    {
        // start message:
        if (data.type === "start")
        {
            // Set subtitle:
            var header = document.getElementById('header');
            header.innerHTML = "Thinking...";

            // Create a new message entry:
            var div = document.createElement('div');
            div.className = 'server-message';
            var p = document.createElement('p');

            // Set temporary message:
            p.innerHTML = "<strong>" + "Omega: " + "</strong> thinking...";

            // Add this new message into message list:
            div.appendChild(p);
            messages.appendChild(div);
        }
        // end message, this is sent once the agent has a response:
        else if (data.type === "end")
        {
            var header = document.getElementById('header');

            // Current (last) message:
            var p = messages.lastChild.lastChild;

            // Parse markdown and render as HTML:
            p.innerHTML = "<strong>" + "Omega: " + "</strong>" + marked.parse(data.message)

            // Reset subtitle:
            var header = document.getElementById('header');
            header.innerHTML = default_subtitle;

            // Reset button text and state:
            var button = document.getElementById('send');
            button.innerHTML = "Send";
            button.disabled = false;
        }
        // Error:
        else if (data.type === "error")
        {
            // Reset subtitle:
            var header = document.getElementById('header');
            header.innerHTML = default_subtitle;

            // Reset button text and state:
            var button = document.getElementById('send');
            button.innerHTML = "Send";
            button.disabled = false;

            // Display error message:
            var p = messages.lastChild.lastChild;
            p.innerHTML = "<strong>" + "Omega: " + "</strong>" + message
        }
    }
    // Message received from user:
    else if (data.sender === "user")
    {
        // Create new message entry:
        var div = document.createElement('div');
        div.className = 'client-message';
        var p = document.createElement('p');

        // Set default (empty) message:
        p.innerHTML = "<strong>" + "You: " + "</strong>";
        p.innerHTML += data.message;

        // Add message to message list:
        div.appendChild(p);
        messages.appendChild(div);
    }
    // Scroll to the bottom of the chat
    messages.scrollTop = messages.scrollHeight;
};


// Send message to server
function sendMessage(event)
{
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