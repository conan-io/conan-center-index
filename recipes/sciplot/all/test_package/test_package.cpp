// sciplot - a modern C++ scientific plotting library powered by gnuplot
// https://github.com/sciplot/sciplot
//
// Licensed under the MIT License <http://opensource.org/licenses/MIT>.
//
// Copyright (c) 2018-2021 Allan Leal
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

// sciplot includes
#include <sciplot/sciplot.hpp>
// #include <sciplot.hpp>
using namespace sciplot;

int main(int argc, char** argv) {
  // Create a vector with x-axis values
  std::vector<int> x = {0, 1, 2, 3};

  // Create a vector with y values
  std::vector<float> y = {-4, 2, 5, -3};

  // Create a Plot object
  Plot2D plot;

  // Set the legend
  plot.legend().hide();

  // Set the x and y labels
  plot.xlabel("x");
  plot.ylabel("y");

  // Set the y range
  plot.yrange(-5, 5);

  // Add values to plot
  plot.drawBoxes(x, y).fillSolid().fillColor("green").fillIntensity(0.5);

  // Adjust the relative width of the boxes
  plot.boxWidthRelative(0.75);

  // Create figure to hold plot
  Figure fig = {{plot}};
  // Create canvas to hold figure
  Canvas canvas = {{fig}};

  // Show the plot in a pop-up window
  canvas.show();

  // Save the plot to a PDF file
  canvas.save("example-boxes.pdf");
}