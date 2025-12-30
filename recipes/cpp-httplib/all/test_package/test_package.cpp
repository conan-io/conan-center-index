// #include <httplib.h>
//
// int main() {
//   httplib::Request request;
//   return 0;
// }
#include <httplib.h>
int main() {
  httplib::Client cli("http://example.com");
  auto res = cli.Get("/");
  return 0;
}
