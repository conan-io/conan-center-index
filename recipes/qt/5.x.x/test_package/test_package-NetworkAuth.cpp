#include <QDebug>
#include <QOAuth1>

int main(int argc, char *argv[]){

    QOAuth1 obj;
    qDebug() << obj.clientSharedSecret();

    return 0;
}
