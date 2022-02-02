cmake_minimum_required(VERSION 3.0.0)
project(axtls)


if(NOT CMAKE_BUILD_TYPE)
   set(CMAKE_BUILD_TYPE Release)
endif()
string(TOUPPER ${CMAKE_BUILD_TYPE} CMAKE_BUILD_TYPE)

include_directories(
	"${CMAKE_SOURCE_DIR}/crypto"
	"${CMAKE_SOURCE_DIR}/ssl"
	"${CMAKE_SOURCE_DIR}/config"
)

set(CRYPTO_SOURCES
	"${CMAKE_SOURCE_DIR}/crypto/aes.c"
	"${CMAKE_SOURCE_DIR}/crypto/bigint.c"
	"${CMAKE_SOURCE_DIR}/crypto/crypto_misc.c"
	"${CMAKE_SOURCE_DIR}/crypto/hmac.c"
	"${CMAKE_SOURCE_DIR}/crypto/md5.c"
	"${CMAKE_SOURCE_DIR}/crypto/rc4.c"
	"${CMAKE_SOURCE_DIR}/crypto/rsa.c"
	"${CMAKE_SOURCE_DIR}/crypto/sha1.c"
	"${CMAKE_SOURCE_DIR}/crypto/sha256.c"
	"${CMAKE_SOURCE_DIR}/crypto/sha384.c"
	"${CMAKE_SOURCE_DIR}/crypto/sha512.c"
)

set(SSL_SOURCES
	"${CMAKE_SOURCE_DIR}/ssl/asn1.c"
	"${CMAKE_SOURCE_DIR}/ssl/gen_cert.c"
	"${CMAKE_SOURCE_DIR}/ssl/loader.c"
	"${CMAKE_SOURCE_DIR}/ssl/openssl.c"
	"${CMAKE_SOURCE_DIR}/ssl/os_port.c"
	"${CMAKE_SOURCE_DIR}/ssl/p12.c"
	"${CMAKE_SOURCE_DIR}/ssl/tls1.c"
	"${CMAKE_SOURCE_DIR}/ssl/tls1_svr.c"
	"${CMAKE_SOURCE_DIR}/ssl/tls1_clnt.c"
	"${CMAKE_SOURCE_DIR}/ssl/x509.c"
)

add_library(axtls SHARED ${SSL_SOURCES} ${CRYPTO_SOURCES})
set_target_properties (axtls PROPERTIES VERSION 1.5 SOVERSION 1)

if (WIN32)
	set(c_flags "/nologo /W3 /FD")
	set(ld_flags "/nologo /subsystem:console")
	set(defines WIN32 _MBCS _CONSOLE _CRT_SECURE_NO_DEPRECATE)
	if (CMAKE_BUILD_TYPE STREQUAL "DEBUG")
		set(c_flags "${c_flags} /Zi /Od")
		list(APPEND defines "_DEBUG")
		set(ld_flags "${ld_flags} /debug /incremental:yes")
	else()
		set(c_flags "${c_flags} /O2")
		set(ld_flags "${ld_flags} /incremental:no")
	endif()
elseif(UNIX)
	set(c_flags "-Wall -Wstrict-prototypes -Wshadow")
	set(ld_flags "")
	set(defines "")
	message("${CMAKE_BUILD_TYPE}")
	if (NOT CMAKE_BUILD_TYPE STREQUAL "DEBUG")
		set(c_flags "${c_flags} -O3")
	else()
		list(APPEND defines "_DEBUG")
	endif()
endif()

set_target_properties(axtls PROPERTIES
	LINK_FLAGS "${ld_flags}"
	COMPILE_FLAGS "${c_flags}"
	COMPILE_DEFINITIONS "${defines}"
)

set(headers
	"crypto/bigint.h"
	"crypto/bigint_impl.h"
	"crypto/crypto.h"
	"crypto/os_int.h"
	"ssl/crypto_misc.h"
	"ssl/ssl.h"
	"ssl/tls1.h"
	"ssl/version.h"
	"ssl/os_port.h"
	"config/config.h"
)

install(TARGETS axtls
        RUNTIME DESTINATION bin
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib
        PRIVATE_HEADER DESTINATION include
        PUBLIC_HEADER DESTINATION include)
install(FILES $<TARGET_PDB_FILE:axtls> DESTINATION bin OPTIONAL)
install(FILES ${headers} DESTINATION "include/axTLS")
