 include($$OUT_PWD/../conanbuildinfo.pri)

 LIBS += $$CONAN_LIBDIRS

 SOURCES += test_package.cpp

HEADERS += greeter.h

QT -= gui

CONFIG += console
