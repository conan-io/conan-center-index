#include <QDebug>
#include <QNetworkAccessManager>

int main(int argc, char *argv[]){

    QNetworkAccessManager networkTester;
    qDebug() << networkTester.supportedSchemes();

    return 0;
}
