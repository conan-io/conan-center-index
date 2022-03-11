#include "rapidcsv.h"

#include <sstream>
#include <string>

int main() {
    std::string csv =
        "City,Temperature\n"
        "Munich,5.4\n"
        "Paris,9.3\n"
        "Rio de Janeiro,20.4\n"
        "New York City,19.9\n"
        "Adelaide,14.5\n";
    std::stringstream stream(csv);
    rapidcsv::Document doc(stream, rapidcsv::LabelParams());
    return 0;
}
