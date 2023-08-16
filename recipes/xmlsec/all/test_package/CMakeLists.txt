cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(xmlsec REQUIRED CONFIG)
find_package(LibXml2 REQUIRED MODULE)
if(XMLSEC_WITH_XSLT)
    find_package(LibXslt REQUIRED MODULE)
endif()

add_executable(${PROJECT_NAME} sign1.c)
target_link_libraries(${PROJECT_NAME} PRIVATE LibXml2::LibXml2 xmlsec::xmlsec)
if(XMLSEC_WITH_XSLT)
    target_link_libraries(${PROJECT_NAME} PRIVATE LibXslt::LibXslt)
endif()
