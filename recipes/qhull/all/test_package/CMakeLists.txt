cmake_minimum_required(VERSION 3.15)
project(test_package)

find_package(Qhull REQUIRED CONFIG)

# Select source and target depending on reentrant flag
if(QHULL_REENTRANT)
    set(TEST_SRC test_package_r.c)
    if(TARGET Qhull::qhull_r)
        set(TEST_LIB Qhull::qhull_r)
    else()
        set(TEST_LIB Qhull::qhullstatic_r)
    endif()
else()
    set(TEST_SRC test_package.c)
    if(TARGET Qhull::libqhull)
        set(TEST_LIB Qhull::libqhull)
    else()
        set(TEST_LIB Qhull::qhullstatic)
    endif()
endif()

# Main C test
add_executable(${PROJECT_NAME} ${TEST_SRC})
target_link_libraries(${PROJECT_NAME} PRIVATE ${TEST_LIB})

# Optional C++ test (only with static builds)
if(TARGET Qhull::qhullcpp)
    add_executable(${PROJECT_NAME}_cpp test_package_cpp.cpp)
    target_link_libraries(${PROJECT_NAME}_cpp PRIVATE ${TEST_LIB} Qhull::qhullcpp)
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
endif()
