#include <cstdlib>
#include <iostream>
#include <qcustomplot.h>


int main(void) {
    QCPVector2D qcp_vector(2, 4);
    qcp_vector.normalize();
    std::cout << "QCustomPlot - vector 2D length: " << qcp_vector.length() << std::endl;
    return EXIT_SUCCESS;
}
