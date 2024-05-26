#include <tcpcat/tcpcat.h>

#include <iostream>
#include <string>

int main()
{
   tcpcat::TcpSession session(nullptr, nullptr, 0);
   std::cout << "session id: " << session.GetId() << std::endl;
   return 0;
}
