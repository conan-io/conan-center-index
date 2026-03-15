#include <QCoreApplication>
#include <QObject>
#include <QString>
#include <QTimer>
#include <QFile>

#include <QNetworkAccessManager>
#ifdef HAVE_QT_SQL
#include <QSqlDatabase>
#endif
#include <qtconcurrentfilter.h>
#ifdef HAVE_QT_XML
#include <QDomText>
#endif

#include "greeter.h"

int main(int argc, char *argv[]){
    QCoreApplication app(argc, argv);
    QCoreApplication::setApplicationName("Application Example");
    QCoreApplication::setApplicationVersion("1.0.0");

    QString name = argc > 0 ? argv[1] : "";
    if (name.isEmpty()) {
        name = "World";
    }

    Greeter* greeter = new Greeter(name, &app);
    QObject::connect(greeter, SIGNAL(finished()), &app, SLOT(quit()));
    QTimer::singleShot(0, greeter, SLOT(run()));

    QFile f(":/resource.txt");
    if(!f.open(QIODevice::ReadOnly))
        qFatal("Could not open resource file");
    qDebug() << "Resource content:" << f.readAll();
    f.close();

    QNetworkAccessManager networkTester;

#ifdef HAVE_QT_SQL
    QSqlDatabase sqlTester;
#endif

    QVector<int> v;
    v << 1 << 2 << 3 << 4;
    QtConcurrent::blockingFilter(v, [](int i)
    {
        return i % 2;
    });

#ifdef HAVE_QT_XML
    QDomText xmlTester;
#endif

    return app.exec();
}
