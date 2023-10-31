#include <QDebug>
#include <QQuickItem>
#include <QtQuickTest>

int main(int argc, char *argv[]){

    QQuickItem quickItem;
    qDebug() << QQuickTest::qIsPolishScheduled( &quickItem );

    return 0;
}
