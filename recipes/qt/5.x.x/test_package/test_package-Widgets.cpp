#include "static_build.h"

#include <QApplication>
#include <QDebug>
#include <QListView>

int main(int argc, char *argv[]){

    QApplication app(argc, argv);
    QListView listView;
    qDebug() << ((listView.movement() == QListView::Static) ? "use default movement" : "use custom movement");
    
    return 0;
}
