#include <lift/lift.hpp>
#include <stdio.h>

int main() {
  printf("************* Testing liblifthttp ***************\n");
  lift::client().start_request(
      std::make_unique<lift::request>("https://google.com/"),
      [](auto request_ptr, auto response) {
        std::cout << "lift status: " << lift::to_string(response.lift_status())
                  << "\n";
        if (response.lift_status() != lift::lift_status::success) {
          std::cout << "network error message: "
                    << response.network_error_message() << "\n";
        }
      });
  printf("OK\n");
  return 0;
}
