#include <cpr/cpr.h>

#include <iostream>

int main(int argc, char** argv) {
    auto r = cpr::Get(cpr::Url{"http://jsonplaceholder.typicode.com/todos/1"}, // https available after 1.5.0 (not windows by default)
        cpr::Parameters{{"Accept", "application/json"}});
    std::cout << "status code: " << r.status_code << '\n';                  // 200
    std::cout << "headers:     " << r.header["content-type"] << '\n';       // application/json; charset=utf-8
    std::cout << "text:        " << r.text << '\n';                         // JSON text string
    return 0;
}
