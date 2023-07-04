#include <QDebug>
#include <QSqlDatabase>

int main(int argc, char *argv[]){

    qDebug() << QSqlDatabase::drivers();
    
    return 0;
}
