
cmake_minimum_required (VERSION 3.15)

project ("Gustave-Package-Test" LANGUAGES "CXX")
set(CMAKE_CXX_STANDARD 20)

find_package(Gustave CONFIG REQUIRED Distrib-Std)

add_executable(Gustave-Package-Test
    "main.cpp"
)
target_link_libraries(Gustave-Package-Test PRIVATE Gustave::Distrib-Std)

add_custom_target(run-test
    COMMAND Gustave-Package-Test
    DEPENDS Gustave-Package-Test
)
