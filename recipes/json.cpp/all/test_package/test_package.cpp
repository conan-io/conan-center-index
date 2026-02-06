#include "json.h"

int main(void) {
    auto [status, json] = jt::Json::parse("{\"value\": 5}");
}
