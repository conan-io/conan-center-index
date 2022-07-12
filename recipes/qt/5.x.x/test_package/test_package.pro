SOURCES += test_package.cpp

HEADERS += greeter.h

RESOURCES = example.qrc

QT -= gui
QT += network sql concurrent xml

CONFIG += console

CONFIG += conan_basic_setup
include($$OUT_PWD/../conanbuildinfo.pri)
LIBS -= $$CONAN_LIBS_QT
