#include <httplib.h>

int main() {
  httplib::Server svr;

  svr.Get("/hi", [](const httplib::Request& req, httplib::Response& res) {
    res.set_content("Hello World!", "text/plain");
  });

  svr.Get(R"(/numbers/(\d+))", [&](const httplib::Request& req, httplib::Response& res) {
    auto numbers = req.matches[1];
    res.set_content(numbers, "text/plain");
  });

  svr.Get("/stop", [&](const httplib::Request& req, httplib::Response& res) {
    svr.stop();
  });

  return 0;
}
