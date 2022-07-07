#include <cppcms/application.h>
#include <cppcms/applications_pool.h>
#include <cppcms/http_response.h>
#include <cppcms/service.h>
#include <iostream>

class hello : public cppcms::application {
public:
  hello(cppcms::service &srv) : cppcms::application(srv) {}
  virtual void main(std::string url);
};

void hello::main(std::string /*url*/) {
  response().out() << "<html>\n"
                      "<body>\n"
                      "  <h1>Hello World</h1>\n"
                      "</body>\n"
                      "</html>\n";
}

int main(int argc, char **argv) {
  try {
    cppcms::service srv(argc, argv);
    srv.applications_pool().mount(cppcms::applications_factory<hello>());
  } catch (std::exception const &e) {
    std::cerr << e.what() << std::endl;
    return 1;
  }
  return 0;
}
