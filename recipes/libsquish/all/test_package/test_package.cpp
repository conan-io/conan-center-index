#include <squish.h>

#include <algorithm>
#include <cmath>
#include <iostream>
#include <limits>

double getColourError(const squish::u8 *a, const squish::u8 *b) {
  double error = 0.0;
  for (int i = 0; i < 16; ++i) {
    for (int j = 0; j < 3; ++j) {
      int index = 4 * i + j;
      int diff = static_cast<int>(a[index]) - static_cast<int>(b[index]);
      error += static_cast<double>(diff * diff);
    }
  }
  return error / 16.0;
}

void testTwoColour(int flags) {
  squish::u8 input[4 * 16];
  squish::u8 output[4 * 16];
  squish::u8 block[16];

  double avg = 0.0;
  double min = std::numeric_limits<double>::max();
  double max = - std::numeric_limits<double>::max();
  int counter = 0;

  // test all single-channel colours
  for (int i = 0; i < 16 * 4; ++i) {
    input[i] = ((i % 4) == 3) ? 255 : 0;
  }

  for (int channel = 0; channel < 3; ++channel) {
    for (int value1 = 0; value1 < 255; ++value1) {
      for (int value2 = value1 + 1; value2 < 255; ++value2) {
        // set the channnel value
        for (int i = 0; i < 16; ++i) {
          input[4 * i + channel] = static_cast<squish::u8>((i < 8) ? value1 : value2);
        }

        // compress and decompress
        squish::Compress(input, block, flags);
        squish::Decompress(output, block, flags);

        // test the results
        double rm = getColourError(input, output);
        double rms = std::sqrt(rm);

        // accumulate stats
        min = std::min(min, rms);
        max = std::max(max, rms);
        avg += rm;
        ++counter;
      }
    }

    // reset the channel value
    for (int i = 0; i < 16; ++i) {
      input[4 * i + channel] = 0;
    }
  }

  // finish stats
  avg = std::sqrt(avg / counter);

  // show stats
  std::cout << "two colour error (min, max, avg): "
            << min << ", " << max << ", " << avg
            << std::endl;
}

int main() {
  testTwoColour(squish::kDxt1);
  return 0;
}
