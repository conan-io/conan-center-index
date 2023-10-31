#include <QDebug>
#include <QTestEventList>

int main(int argc, char *argv[]){

    QTestEventList obj;
    qDebug() << &obj;

    return 0;
}
