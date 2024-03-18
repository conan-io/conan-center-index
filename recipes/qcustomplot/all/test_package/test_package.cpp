#include <qcustomplot.h>
#include <iostream>


int main(int argc, char *argv[]) {
    QCPVector2D vec(1,2);
    vec = vec.normalized();
    vec *= 2;
    cout << vec.length();
    return 0;
}
