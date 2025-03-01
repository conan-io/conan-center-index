#include <cstdlib>
#include <iostream>
#include <string>
#include <opentrackio-cpp/OpenTrackIOSample.h>


int main(void) {
    std::string example = R"({
      "protocol": {
        "name": "OpenTrackIO",
        "version": "1.0.0"
      },
      "tracker": {
        "notes": "Example generated sample.",
        "recording": false,
        "slate": "A101_A_4",
        "status": "Optical Good"
      }
    })";
    
    opentrackio::OpenTrackIOSample sample{};
    bool sample_success = sample.initialise(std::string_view{example});
    std::cout << "Sample init successful: " << (sample_success ? "True" : "False") << std::endl;
    return EXIT_SUCCESS;
}
