#include <QDebug>
#include <QWebChannel>

int main(int argc, char *argv[]){

    QWebChannel obj;
    qDebug() << obj.blockUpdates();
        
    return 0;
}
