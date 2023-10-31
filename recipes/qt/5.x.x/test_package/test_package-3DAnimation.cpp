#include <QDebug>
#include <Qt3DAnimation/QChannel>

int main(int argc, char *argv[]){

    Qt3DAnimation::QChannel obj;
    qDebug() << obj.name();
        
    return 0;
}
