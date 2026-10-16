#include <DockManager.h>
#include <QDebug>
#include <QFile>

#ifdef EXPECTED_ADS_VERSION
#include <ads_version.h>
static_assert(ADS_VERSION == EXPECTED_ADS_VERSION, "Incorrect ADS version header");
#endif

int main(int argc, char *argv[])
{
    qDebug() << ads::CDockManager::configFlags();

#ifdef EXPECTED_ADS_VERSION
    for (const auto* path : {":/ads/stylesheets/default_dark.css",
                             ":/ads/stylesheets/default_linux_dark.css",
                             ":/ads/images/close-button_dark.svg"})
    {
        QFile resource(path);
        if (!resource.open(QIODevice::ReadOnly) || resource.readAll().isEmpty())
        {
            qCritical() << "Missing or empty ADS resource:" << path;
            return 1;
        }
    }
#endif

    return 0;
}
