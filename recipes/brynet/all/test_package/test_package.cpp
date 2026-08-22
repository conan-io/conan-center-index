#include <brynet/net/TcpService.hpp>

int main() {
#ifdef BRYNET_EVENTLOOP_TCPSERVICE
    // brynet >= 1.11.2 provides IOThreadTcpService and EventLoopTcpService instead of TcpService
    auto service = brynet::net::IOThreadTcpService::Create();
#else
    auto service = brynet::net::TcpService::Create();
#endif
    return 0;
}
