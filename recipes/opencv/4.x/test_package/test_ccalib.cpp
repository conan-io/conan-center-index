#include <opencv2/ccalib/randpattern.hpp>

int main() {
    cv::randpattern::RandomPatternGenerator generator(50, 50);
    generator.generatePattern();
    auto pattern = generator.getPattern();
    return 0;
}
