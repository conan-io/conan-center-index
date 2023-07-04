#include <QDebug>
#include <QQuickItem>

int main(int argc, char *argv[]){

    QQuickItem item;
    qDebug() << item.state();

    return 0;
}
