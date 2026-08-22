#include <cstdlib>

#include "essentials/log/log.hpp"

int main() {

    auto& logger = sxe::logger::get_instance();
	sxe::logger_manager::get_instance().set_logger( logger );
	logger.set_log_level( LL_TRACE );
	logger.add_std_out_sink();

    SXE_LOG_LOCATED( LL_TRACE, "main.cpp", __LINE__, "{}) Hello {}!", __LINE__, "John Doe" );
	SXE_LOG_LOCATED( LL_DEBUG, "main.cpp", __LINE__, "{}) Hello {}!", __LINE__, "John Doe" );
	SXE_LOG_LOCATED( LL_INFO,  "main.cpp", __LINE__, "{}) Hello {}!", __LINE__, "John Doe" );
	SXE_LOG_LOCATED( LL_WARN,  "main.cpp", __LINE__, "{}) Hello {}!", __LINE__, "John Doe" );
	SXE_LOG_LOCATED( LL_ERROR, "main.cpp", __LINE__, "{}) Hello {}!", __LINE__, "John Doe" );
	SXE_LOG_LOCATED( LL_FATAL, "main.cpp", __LINE__, "{}) Hello {}!", __LINE__, "John Doe" );
    
    return EXIT_SUCCESS;
}
