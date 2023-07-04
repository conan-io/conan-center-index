#include <QtConcurrent>
#include <QDebug>

int main(int argc, char *argv[])
{
    QFuture<void> future = QtConcurrent::run( [](){ qDebug() << "inside QtConcurrent"; } );
    future.waitForFinished();
  
    return 0;
}
