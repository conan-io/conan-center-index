#include <cpprest/json.h>

int main()
{
    const auto parsed_value = web::json::value::parse(U("-22"));
}
