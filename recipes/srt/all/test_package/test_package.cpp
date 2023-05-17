#include <srt/srt.h>

#ifndef _WIN32
   #include <cstdlib>
   #include <netdb.h>
#else
   #include <winsock2.h>
   #include <ws2tcpip.h>
#endif

#include <string>

int main()
{
   // use this function to initialize the UDT library
   srt_startup();

   srt_setloglevel(srt_logging::LogLevel::debug);
   addrinfo hints;
   addrinfo* res;

   memset(&hints, 0, sizeof(struct addrinfo));
   hints.ai_flags = AI_PASSIVE;
   hints.ai_family = AF_INET;
   hints.ai_socktype = SOCK_DGRAM;

   std::string service("9000");
   if (0 != getaddrinfo(NULL, service.c_str(), &hints, &res))
   {
      srt_cleanup();
      return 1;
   }

   SRTSOCKET serv = srt_socket(res->ai_family, res->ai_socktype, res->ai_protocol);
   srt_close(serv);

   // use this function to release the UDT library
   freeaddrinfo(res);
   srt_cleanup();
   return 0;
}
