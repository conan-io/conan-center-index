#include <QDebug>
#include <Qt3DExtras/QConeMesh>

int main(int argc, char *argv[]){

    Qt3DExtras::QConeMesh obj;
    qDebug() << obj.rings();
        
    return 0;
}
