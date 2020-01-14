#include <iostream>
#include <ixwebsocket/IXWebSocket.h>
#include <string>
#include <vector>
#include <chrono>
#include <thread>
#include <ixwebsocket/IXNetSystem.h>
#include <ixwebsocket/IXSocketTLSOptions.h>

class SocketWrapper {
private:
    ix::WebSocket webSocket;
    std::vector<std::string> receivedMessages;
public:
    SocketWrapper() {
        webSocket.setUrl(std::string("ws://echo.websocket.org"));
        webSocket.setOnMessageCallback(
            [this](const ix::WebSocketMessagePtr& message) {
                std::cout << "Something received" << std::endl;
                if (message->type == ix::WebSocketMessageType::Open) {
                    std::cout << "Connected\n";
                    //webSocket.send(std::string("Congrats, your local version of IXWebSocket works!"));
                } else if (message->type == ix::WebSocketMessageType::Close) {
                    std::cout << "Closing socket...\n";
                } else if (message->type == ix::WebSocketMessageType::Message) {
                    std::cout << "Message received from server: " << message->str << std::endl;
                    receivedMessages.push_back(message->str);
                } else if (message->type == ix::WebSocketMessageType::Error) {
                    std::cout << "ERROR:" << message->errorInfo.reason;
                } 
            });

        webSocket.start();

    }

    bool hasReceived() { return receivedMessages.size() > 0; }
    void close() { this->webSocket.close(); }
    bool ready() { 
        return this->webSocket.getReadyState() == ix::ReadyState::Open; 
    }
    void send(std::string message) { this->webSocket.send(message); }
};

int main() {
    try {
        std::cout << "Starting socket..." << std::endl;
        ix::initNetSystem(); // required for Windows
        SocketWrapper socketWrapper;
        int counter = 0;
        while(true) {
            std::this_thread::sleep_for(std::chrono::milliseconds(2000));
            if (!socketWrapper.ready())
                continue;
            counter++;
            if (socketWrapper.hasReceived()) {
                break;
            } else if (counter >= 5) {
                socketWrapper.close();
                ix::uninitNetSystem();
                std::cout << "No response for 10 seconds; assuming failure" << std::endl;
                throw std::string("No response for 10 seconds: assuming failure");
            }

            if (socketWrapper.ready()) {
                std::cout << "Sent message." << std::endl;
                socketWrapper.send("Congrats, your local version of IXWebSocket works!");
            }
        }
        std::cout << "Message received! Closing socket." << std::endl;
        socketWrapper.close();
        std::cout << "Socket disconnected." << std::endl;

        ix::uninitNetSystem(); // required for Windows.

    } catch (const char* ex) {
        std::cout << ex;
        throw;
    }
}
