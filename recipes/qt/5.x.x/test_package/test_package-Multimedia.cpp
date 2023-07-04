#include <QDebug>
#include <QCameraInfo>

int main(int argc, char *argv[]){

    QCameraInfo cameraInfo;
    qDebug() << (cameraInfo.isNull() ? "No camera info available" : cameraInfo.description() );
        
    return 0;
}
