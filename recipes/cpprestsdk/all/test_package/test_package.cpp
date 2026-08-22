#include <cpprest/http_msg.h>
#include <cpprest/http_client.h>

int main()
{
    const auto parsed_value = web::json::value::parse(U("-22"));
    const auto get_method = web::http::methods::GET;
}
