cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

set(BITSERIALIZER_COMPONENTS core)
if(WITH_CPPRESTSDK)
    list(APPEND BITSERIALIZER_COMPONENTS cpprestjson-archive)
endif()
if(WITH_RAPIDJSON)
    list(APPEND BITSERIALIZER_COMPONENTS rapidjson-archive)
endif()
if(WITH_PUGIXML)
    list(APPEND BITSERIALIZER_COMPONENTS pugixml-archive)
endif()
if(WITH_RAPIDYAML)
    list(APPEND BITSERIALIZER_COMPONENTS rapidyaml-archive)
endif()
if(WITH_CSV)
    list(APPEND BITSERIALIZER_COMPONENTS csv-archive)
endif()
if(WITH_MSGPACK)
    list(APPEND BITSERIALIZER_COMPONENTS msgpack-archive)
endif()

find_package(bitserializer CONFIG REQUIRED
    COMPONENTS ${BITSERIALIZER_COMPONENTS}
)

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
target_link_libraries(${PROJECT_NAME} PRIVATE
    BitSerializer::core
    $<$<BOOL:${WITH_CPPRESTSDK}>:BitSerializer::cpprestjson-archive>
    $<$<BOOL:${WITH_RAPIDJSON}>:BitSerializer::rapidjson-archive>
    $<$<BOOL:${WITH_PUGIXML}>:BitSerializer::pugixml-archive>
    $<$<BOOL:${WITH_RAPIDYAML}>:BitSerializer::rapidyaml-archive>
    $<$<BOOL:${WITH_CSV}>:BitSerializer::csv-archive>
    $<$<BOOL:${WITH_MSGPACK}>:BitSerializer::msgpack-archive>
)
target_compile_definitions(${PROJECT_NAME} PRIVATE
    $<$<BOOL:${WITH_CPPRESTSDK}>:"WITH_CPPRESTSDK">
    $<$<BOOL:${WITH_RAPIDJSON}>:"WITH_RAPIDJSON">
    $<$<BOOL:${WITH_PUGIXML}>:"WITH_PUGIXML">
    $<$<BOOL:${WITH_RAPIDYAML}>:"WITH_RAPIDYAML">
    $<$<BOOL:${WITH_CSV}>:"WITH_CSV">
    $<$<BOOL:${WITH_MSGPACK}>:"WITH_MSGPACK">
)
