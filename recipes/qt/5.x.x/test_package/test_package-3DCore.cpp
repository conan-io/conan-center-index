#include <QDebug>
#include <QTransform>

int main(int argc, char *argv[]){

    Qt3DCore::QTransform obj;
    qDebug() << obj.rotation();
        
    return 0;
}
