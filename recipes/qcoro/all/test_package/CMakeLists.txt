cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(QCoro6 REQUIRED COMPONENTS Core)
qcoro_enable_coroutines()

if(MSVC)
    # Qt6Core.lib(qlocale_win.cpp.obj) : error LNK2038: mismatch detected for '_COROUTINE_ABI': value '1' doesn't match value '2' in test_package.obj
    # https://stackoverflow.com/questions/70348706/error-lnk2038-mismatch-detected-for-coroutine-abi-value-2-doesnt-match-v
    # https://devblogs.microsoft.com/oldnewthing/20230111-00/?p=107694
    add_compile_definitions(_ALLOW_COROUTINE_ABI_MISMATCH)
endif()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} QCoro6::Core Qt6::Concurrent)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)
