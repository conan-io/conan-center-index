 include($$OUT_PWD/../conanbuildinfo.pri)

 LIBS += $$CONAN_LIBDIRS

 SOURCES += test_package.cpp

HEADERS += greeter.h

RESOURCES = example.qrc

QT += network sql concurrent xml dbus

QT -= gui

CONFIG += console
