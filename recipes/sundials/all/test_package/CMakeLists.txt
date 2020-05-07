cmake_minimum_required(VERSION 2.8.12)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

if (WITH_CVODE)
    add_executable(test_cvode test_cvode.cpp)
    target_link_libraries(test_cvode ${CONAN_LIBS})
endif()

if (WITH_CVODES)
    add_executable(test_cvodes test_cvodes.cpp)
    target_link_libraries(test_cvodes ${CONAN_LIBS})
endif()

if (WITH_ARKODE)
    add_executable(test_arkode test_arkode.cpp)
    target_link_libraries(test_arkode ${CONAN_LIBS})
endif()

if (WITH_IDA)
    add_executable(test_ida test_ida.cpp)
    target_link_libraries(test_ida ${CONAN_LIBS})
endif()

if (WITH_IDAS)
    add_executable(test_idas test_idas.cpp)
    target_link_libraries(test_idas ${CONAN_LIBS})
endif()

if (WITH_KINSOL)
    add_executable(test_kinsol test_kinsol.cpp)
    target_link_libraries(test_kinsol ${CONAN_LIBS})
endif()
