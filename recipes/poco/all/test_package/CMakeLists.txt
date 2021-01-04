cmake_minimum_required(VERSION 3.1)
project(MyHello)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(CMAKE_CXX_STANDARD 11)

add_executable(core test_core.cpp)
target_link_libraries(core ${CONAN_LIBS})

option(TEST_NET "Test Net")
if(TEST_NET)
    add_executable(net test_net.cpp)
    target_link_libraries(net ${CONAN_LIBS})

    add_executable(net_2 test_net_2.cpp)
    target_link_libraries(net_2 ${CONAN_LIBS})
endif()

option(TEST_NETSSL "Test NetSSL")
if(TEST_NETSSL)
    add_executable(netssl test_netssl.cpp)
    target_link_libraries(netssl ${CONAN_LIBS})
endif()

option(TEST_CRYPTO "Test crypto")
if(TEST_CRYPTO)
    add_executable(tcrypto test_crypto.cpp)
    target_link_libraries(tcrypto ${CONAN_LIBS})
    set_property(TARGET tcrypto PROPERTY OUTPUT_NAME "crypto")
endif()

option(TEST_UTIL "Test Util")
if(TEST_UTIL)
    add_executable(util test_util.cpp)
    target_link_libraries(util ${CONAN_LIBS})
    if(MINGW)
        target_link_options(util PRIVATE -municode)
    endif()
endif()

option(TEST_SQLITE "Test Sqlite")
if(TEST_SQLITE)
    add_executable(sqlite test_sqlite.cpp)
    target_link_libraries(sqlite ${CONAN_LIBS})
endif()

option(TEST_ENCODINGS "Test Encodings")
if(TEST_ENCODINGS)
    add_executable(encodings test_encodings.cpp)
    target_link_libraries(encodings ${CONAN_LIBS})
endif()

option(TEST_JWT "Test JWT")
if(TEST_JWT)
    add_executable(jwt test_jwt.cpp)
    target_link_libraries(jwt ${CONAN_LIBS})
endif()
