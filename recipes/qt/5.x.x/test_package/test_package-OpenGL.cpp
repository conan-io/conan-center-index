#include <QDebug>
#include <QGL>

int main(int argc, char *argv[]){

    QGLFormat obj;
    qDebug() << obj.samples();

    return 0;
}
