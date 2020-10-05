#include <iostream>
#include <zzip/zzip.h>
#include <zzip/plugin.h>

int main()
{
	zzip_plugin_io_t plugin = ::zzip_get_default_io();
	std::cout << "zzip code 0 means " << zzip_strerror(0) << std::endl;
	return plugin == 0;
}
