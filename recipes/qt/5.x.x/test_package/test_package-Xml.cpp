#include <QDebug>
#include <QDomText>

int main(int argc, char *argv[]){

    QDomText xmlTester;
    qDebug() << static_cast<unsigned int>( xmlTester.nodeType() );
        
    return 0;
}
