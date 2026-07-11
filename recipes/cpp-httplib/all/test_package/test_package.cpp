#include <httplib.h>

int main(int argc, char **) {
  httplib::Request request;

  // Reference the client request path so the linker pulls in
  // getaddrinfo_with_timeout(). With CPPHTTPLIB_USE_NON_BLOCKING_GETADDRINFO
  // this compiles the CFHost resolver on Apple platforms, which fails to link
  // unless CoreFoundation/CFNetwork are provided by the package. The call is
  // guarded so no real network request is made at runtime.
  if (argc > 100) {
    httplib::Client client("http://localhost");
    client.Get("/");
  }

  return 0;
}
