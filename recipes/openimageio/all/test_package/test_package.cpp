#include <OpenImageIO/imagecache.h>
#include <algorithm>

int main()
{
    std::string formats = OIIO::get_string_attribute("format_list");
    std::cout << "Supported formats:\n" << formats;
}
