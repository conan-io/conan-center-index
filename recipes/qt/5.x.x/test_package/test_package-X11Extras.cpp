#include <QDebug>
#include <QX11Info>

int main(int argc, char *argv[]){

    qDebug() << QX11Info::isPlatformX11();
        
    return 0;
}
