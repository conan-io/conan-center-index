#include <CvPlot/cvplot.h>

using namespace CvPlot;

int main() {
	Axes axes = plot(std::vector<double>{ 3, 3, 4, 6, 4, 3 }, "-o");
	cv::Mat mat = axes.render(400, 600);
    return 0;
}
