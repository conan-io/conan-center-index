#include <qcustomplot.h>

#include <QVector>

void dummy()
{
    QCustomPlot customPlot;

    QVector<double> x(101), y(101);
    for (int i = 0; i < 101; ++i)
    {
        x[i] = i / 50.0 - 1;
        y[i] = x[i] * x[i];
    }
    customPlot.addGraph();
    customPlot.graph(0)->setData(x, y);
    customPlot.xAxis->setLabel("x");
    customPlot.yAxis->setLabel("y");
    customPlot.rescaleAxes();
}

int main(int argc, char *argv[])
{
    return 0;
}
