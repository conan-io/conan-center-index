#ifndef TEST_PACKAGE_STATIC_BUILD
#define TEST_PACKAGE_STATIC_BUILD

#ifdef TEST_PACKAGE_USE_QT_STATIC
#    include <QtPlugin>
Q_IMPORT_PLUGIN(QMinimalIntegrationPlugin)
#endif

#endif // TEST_PACKAGE_STATIC_BUILD
