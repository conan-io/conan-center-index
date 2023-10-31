#include <QDebug>
#include <QFrameAction>

int main(int argc, char *argv[]){

    Qt3DLogic::QFrameAction obj;
    qDebug() << &obj;
        
    return 0;
}
