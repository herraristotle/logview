var ws;
var reconnectInterval = 5000; // 5 seconds
var messages = document.createElement('ul');

function connectWebSocket() {
    ws = new WebSocket("ws://172.22.51.121:5678");
    //  ws = new WebSocket(`ws://${window.location.hostname}:5678`);

    
    ws.onopen = function() {
        console.log("WebSocket connection established");
    };

    ws.onmessage = function (event) {
        var message = document.createElement('li'),
            content = document.createTextNode(event.data);
        
        if (event.data === "ping") {
            console.log("Received ping, sending pong");
            ws.send("pong");
        } else {
            message.appendChild(content);
            messages.appendChild(message);
        }
    };

    ws.onerror = function(error) {
        console.error("WebSocket error:", error);
    };

    ws.onclose = function(event) {
        console.log("WebSocket connection closed. Reconnecting...");
        setTimeout(connectWebSocket, reconnectInterval);
    };
}

connectWebSocket();

// Append messages ul to the body only once
if (!document.body.contains(messages)) {
    document.body.appendChild(messages);
}
