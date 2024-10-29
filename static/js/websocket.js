// websocket.js

export class WebSocketClient {
    constructor(url, messageHandler, closeHandler) {
        this.socket = new WebSocket(url);
        this.socket.onmessage = messageHandler;
        this.socket.onclose = closeHandler;
    }

    send(data) {
        this.socket.send(JSON.stringify(data));
    }
}
