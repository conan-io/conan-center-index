#include <mock-services/rest_server.h>
#include <httplib.h>
#include <cassert>
#include <chrono>
#include <iostream>
#include <thread>

int main() {
    // Create a REST mock server (port is auto-assigned)
    mock_services::rest_server server;

    // Configure a route handler: when a GET /hello is received, respond with 200
    server.when("GET", "/hello")
        .then_return(
            mock_services::response_builder{}
                .status(200)
                .body(R"({"message":"Hello, mock-services!"})")
        );

    // Start the server
    server.start();

    // Retrieve the dynamically assigned base URL
    std::string base_url = server.base_url();
    std::cout << "Server running at " << base_url << std::endl;

    // Give the server a moment to bind and start listening
    std::this_thread::sleep_for(std::chrono::milliseconds(200));

    // Make an HTTP request to the mock server using cpp-httplib
    httplib::Client client(base_url);
    auto res = client.Get("/hello");

    assert(res != nullptr);
    assert(res->status == 200);
    std::cout << "Response: " << res->body << std::endl;

    // Verify the request was recorded
    auto requests = server.requests();
    assert(requests.size() == 1);
    assert(requests[0].method == "GET");
    assert(requests[0].path == "/hello");

    // Stop the server
    server.stop();

    std::cout << "mock-services test_package passed!" << std::endl;
    return 0;
}
