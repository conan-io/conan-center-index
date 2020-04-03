#include <DataFrame/DataFrame.h>
#include <cassert>

using namespace hmdf;

typedef StdDataFrame<unsigned long> MyDataFrame;

int main(int argc, char *argv[]) {

  MyDataFrame::set_thread_level(10);

  MyDataFrame df;

  std::vector<int> intvec = {1, 2, 3, 4, 5};
  std::vector<double> dblvec = {1.2345, 2.2345, 3.2345, 4.2345, 5.2345};
  std::vector<double> dblvec2 = {0.998,   0.3456, 0.056,   0.15678,
                                 0.00345, 0.923,  0.06743, 0.1};
  std::vector<std::string> strvec = {"Col_name", "Col_name", "Col_name",
                                     "Col_name", "Col_name"};
  std::vector<unsigned long> ulgvec = {1UL, 2UL, 3UL, 4UL, 5UL, 8UL, 7UL, 6UL};
  std::vector<unsigned long> xulgvec = ulgvec;
  const size_t total_count = ulgvec.size() + intvec.size() + dblvec.size() +
                             dblvec2.size() + strvec.size() + xulgvec.size() +
                             9; // NaNa inserterd

  MyDataFrame::size_type rc = df.load_data(
      std::move(ulgvec), std::make_pair("int_col", intvec),
      std::make_pair("dbl_col", dblvec), std::make_pair("dbl_col_2", dblvec2),
      std::make_pair("str_col", strvec), std::make_pair("ul_col", xulgvec));

  assert(rc == 48);

  return 0;
}
