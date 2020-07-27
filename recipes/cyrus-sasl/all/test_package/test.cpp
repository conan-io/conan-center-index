#include <iostream>
#include <sasl/sasl.h>

int main(int argc, char *argv[])
{
    const char *implementation, *version;
    sasl_version_info(&implementation, &version, NULL, NULL, NULL, NULL);
    std::cout << std::endl
              << "--------------------------->Tests are done.<--------------------------" << std::endl
              << "SASL Using implementation: " << implementation << ", version: " << version << std::endl
              << "//////////////////////////////////////////////////////////////////////" << std::endl;
    return 0;
}
