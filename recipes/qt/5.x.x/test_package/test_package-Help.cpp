#include <QDebug>
#include <QHelpEngine>

int main(int argc, char *argv[]){

    QHelpEngine obj{"test"};
    qDebug() << obj.contentModel();

    return 0;
}
