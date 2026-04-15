#include <iostream>

#include "swaggercpp/swaggercpp.hpp"

int main() {
    auto document = swaggercpp::DocumentReader::read(R"({
      "openapi": "3.1.0",
      "info": { "title": "Conan", "version": "1.0.0" },
      "paths": {
        "/health": {
          "get": {
            "responses": {
              "200": { "description": "ok" }
            }
          }
        }
      }
    })");

    if (!document) {
        return 1;
    }

    std::cout << document.value().info.title << '\n';
    return 0;
}
