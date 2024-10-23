#include <cstdlib>
#include <iostream>
#include <string>
#include <opentrackio-cpp/OpenTrackIOSample.h>


int main(void) {
    std::string example = R"({
      "protocol": {
        "name": "OpenTrackIO",
        "version": "0.9.0"
      },
      "tracker": {
        "notes": "Example generated sample.",
        "recording": false,
        "slate": "A101_A_4",
        "status": "Optical Good"
      }
    })"
    
    opentrackio::OpenTrackIOSample sample{};
    sample.initialise(example);
    return EXIT_SUCCESS;
}
