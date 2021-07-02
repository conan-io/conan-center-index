#include <zimg.h>
#include <iostream>

int main()
{
    unsigned major, minor;
    zimg_get_api_version(&major, &minor);
    std::cout << "zimg version " << major << "." << minor << "\n";
    return 0;
}
