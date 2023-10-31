#include <QDebug>
#include <Qt3DRender/QAttribute>

int main(int argc, char *argv[]){

    Qt3DRender::QAttribute obj;
    qDebug() << obj.name();
        
    return 0;
}
