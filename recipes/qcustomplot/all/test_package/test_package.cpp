#include <cstdlib>
#include <iostream>
#include <qcustomplot.h>


int main(void) {
#if QCUSTOMPLOT_MAJOR_VERSION > 1
    QCPVector2D qcp_vector(2, 4);
#else
    QCPRange qcp_vector(2, 4);
#endif

    qcp_vector.normalize();

#if QCUSTOMPLOT_MAJOR_VERSION > 1
    std::cout << "QCustomPlot - vector 2D length: " << qcp_vector.length() << std::endl;
#else
    std::cout << "QCustomPlot - range size: " << qcp_vector.size() << std::endl;
#endif

    return EXIT_SUCCESS;
}
