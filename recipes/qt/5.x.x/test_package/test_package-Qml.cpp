#include <QDebug>
#include <QQmlError>

int main(int argc, char *argv[]){

    QQmlError error;
    qDebug() << error.column();

    return 0;
}
