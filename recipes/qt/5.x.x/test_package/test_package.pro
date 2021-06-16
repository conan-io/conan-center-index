SOURCES += test_package.cpp

HEADERS += greeter.h

RESOURCES = example.qrc

QT += core widgets gui network concurrent

CONFIG += console

CONFIG += conan_basic_setup
include($$OUT_PWD/../conanbuildinfo.pri)
