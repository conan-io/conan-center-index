#include <QDebug>
#include <QAxis>

int main(int argc, char *argv[]){

    Qt3DInput::QAxis obj;
    qDebug() << obj.value();
        
    return 0;
}
