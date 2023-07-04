#include <QDebug>
#include <QWebSocket>

int main(int argc, char *argv[]){

    QWebSocket obj;
    qDebug() << obj.closeReason();
        
    return 0;
}
