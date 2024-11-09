// websocket.js

export class WebSocketClient {
    constructor(url, messageHandler, closeHandler) {
        this.socket = new WebSocket(url);
        this.socket.onopen = () => {
            console.log("WebSocket connection established.");
        };
        this.socket.onmessage = messageHandler;
        this.socket.onclose = closeHandler;
        this.socket.onerror = this.handleError.bind(this);
    }

    send(data) {
        this.socket.send(JSON.stringify(data));
    }

    handleError(error) {
        console.error("WebSocket error:", error);
    }
}
