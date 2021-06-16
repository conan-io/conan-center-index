#include <QGuiApplication>
#include <QObject>
#include <QString>
#include <QTimer>
#include "greeter.h"
#include <QFile>
#include <QPainter>
#include <QNetworkAccessManager>

void drawPixmapFragments()
{
    QPixmap origPixmap(20, 20);
    QPixmap resPixmap(20, 20);
    QPainter::PixmapFragment fragments[4] = { {15, 15,  0,  0, 10, 10, 1, 1, 0, 1},
                                              { 5, 15, 10,  0, 10, 10, 1, 1, 0, 1},
                                              {15,  5,  0, 10, 10, 10, 1, 1, 0, 1},
                                              { 5,  5, 10, 10, 10, 10, 1, 1, 0, 1} };
    {
        QPainter p(&origPixmap);
        p.fillRect(0, 0, 10, 10, Qt::red);
        p.fillRect(10, 0, 10, 10, Qt::green);
        p.fillRect(0, 10, 10, 10, Qt::blue);
        p.fillRect(10, 10, 10, 10, Qt::yellow);
    }
    {
        QPainter p(&resPixmap);
        p.drawPixmapFragments(fragments, 4, origPixmap);
    }

    QImage origImage = origPixmap.toImage().convertToFormat(QImage::Format_ARGB32);
    QImage resImage = resPixmap.toImage().convertToFormat(QImage::Format_ARGB32);
    QPainter::PixmapFragment fragment = QPainter::PixmapFragment::create(QPointF(20, 20), QRectF(30, 30, 2, 2));
}

int main(int argc, char *argv[]){
    QGuiApplication app(argc, argv);
    QGuiApplication::setApplicationName("Application Example");
    QGuiApplication::setApplicationVersion("1.0.0");

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

    drawPixmapFragments();

    QNetworkAccessManager testNetworkModule;

    return app.exec();
}
