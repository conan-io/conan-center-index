#include "server/asio/tcp_client.h"
#include "server/asio/tcp_server.h"
#include "threads/thread.h"

#include <memory>

class ChatSession : public CppServer::Asio::TCPSession
{
public:
    using CppServer::Asio::TCPSession::TCPSession;
};

class ChatServer : public CppServer::Asio::TCPServer
{
public:
    using CppServer::Asio::TCPServer::TCPServer;
protected:
    std::shared_ptr<CppServer::Asio::TCPSession> CreateSession(
        const std::shared_ptr<CppServer::Asio::TCPServer>& server) override
    {
        return std::make_shared<ChatSession>(server);
    }
};

int main()
{
    auto service = std::make_shared<CppServer::Asio::Service>();
    auto server = std::make_shared<ChatServer>(service, 6667);
}
