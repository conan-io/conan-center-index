#include <DataFrame/DataFrame.h>
#include <DataFrame/DataFrameFinancialVisitors.h>
#include <DataFrame/DataFrameMLVisitors.h>
#include <DataFrame/DataFrameOperators.h>
#include <DataFrame/DataFrameStatsVisitors.h>
#include <DataFrame/GroupbyAggregators.h>
#include <DataFrame/RandGen.h>

#include <cassert>
#include <cmath>
#include <iostream>
#include <limits>
#include <string>
#include <typeinfo>

using namespace hmdf;

typedef StdDataFrame<unsigned long> MyDataFrame;

// -----------------------------------------------------------------------------

static void test_haphazard()  {

    MyDataFrame::set_thread_level(10);

    std::cout << "\nTesting load_data ..." << std::endl;

    MyDataFrame         df;
    std::vector<int>    &col0 =
        df.create_column<int>(static_cast<const char *>("col_name"));

    std::vector<int>            intvec = { 1, 2, 3, 4, 5 };
    std::vector<double>         dblvec =
        { 1.2345, 2.2345, 3.2345, 4.2345, 5.2345 };
    std::vector<double>         dblvec2 =
        { 0.998, 0.3456, 0.056, 0.15678, 0.00345, 0.923, 0.06743, 0.1 };
    std::vector<std::string>    strvec =
        { "Col_name", "Col_name", "Col_name", "Col_name", "Col_name" };
    std::vector<unsigned long>  ulgvec =
        { 1UL, 2UL, 3UL, 4UL, 5UL, 8UL, 7UL, 6UL };
    std::vector<unsigned long>  xulgvec = ulgvec;
    const size_t                total_count =
        ulgvec.size() +
        intvec.size() +
        dblvec.size() +
        dblvec2.size() +
        strvec.size() +
        xulgvec.size() +
        9;  // NaN inserterd

    MyDataFrame::size_type  rc =
        df.load_data(std::move(ulgvec),
                     std::make_pair("int_col", intvec),
                     std::make_pair("dbl_col", dblvec),
                     std::make_pair("dbl_col_2", dblvec2),
                     std::make_pair("str_col", strvec),
                     std::make_pair("ul_col", xulgvec));

    assert(rc == 48);

    df.load_index(ulgvec.begin(), ulgvec.end());
    df.load_column<int>("int_col", { intvec.begin(), intvec.end() },
                        nan_policy::pad_with_nans);
    df.load_column<std::string>("str_col", { strvec.begin(), strvec.end() },
                                nan_policy::pad_with_nans);
    df.load_column<double>("dbl_col", { dblvec.begin(), dblvec.end() },
                           nan_policy::pad_with_nans);
    df.load_column<double>("dbl_col_2", { dblvec2.begin(), dblvec2.end() },
                           nan_policy::dont_pad_with_nans);

    df.append_column<std::string>("str_col", "Additional column");
    df.append_column("dbl_col", 10.56);

    std::vector<int>    ivec = df.get_column<int> ("int_col");

    assert(df.get_column<double> ("dbl_col")[2] == 3.2345);

    std::cout << "\nTesting Visitors 1 ..." << std::endl;

    MeanVisitor<int>    ivisitor;
    MeanVisitor<double> dvisitor;
    const MyDataFrame   const_df = df;
    auto                const_fut =
        const_df.visit_async<int>("int_col", ivisitor);

    assert(const_fut.get().get_result() == 1);

    auto    fut = df.visit_async<double>("dbl_col", dvisitor);

    assert(abs(fut.get().get_result() - 3.2345) < 0.00001);

    df.get_column<double>("dbl_col")[5] = 6.5;
    df.get_column<double>("dbl_col")[6] = 7.5;
    df.get_column<double>("dbl_col")[7] = 8.5;
    assert(::abs(df.visit<double>("dbl_col", dvisitor).get_result() -
                 4.83406) < 0.0001);

    std::vector<double> dvec = df.get_column<double> ("dbl_col");
    std::vector<double> dvec2 = df.get_column<double> ("dbl_col_2");

    assert(dvec.size() == 9);
    assert(dvec[0] == 1.2345);
    assert(dvec[1] == 2.2345);
    assert(dvec[3] == 4.2345);
    assert(dvec[8] == 10.56);

    assert(dvec2.size() == 8);
    assert(dvec2[0] == 0.998);
    assert(dvec2[1] == 0.3456);
    assert(dvec2[4] == 0.00345);
    assert(dvec2[7] == 0.1);

    std::cout << "\nTesting make_consistent ..." << std::endl;

    df.make_consistent<int, double, std::string>();
    df.shrink_to_fit<int, double, std::string>();
    dvec = df.get_column<double> ("dbl_col");
    dvec2 = df.get_column<double> ("dbl_col_2");

    assert(dvec.size() == 8);
    assert(dvec[0] == 1.2345);
    assert(dvec[1] == 2.2345);
    assert(dvec[3] == 4.2345);
    assert(dvec[7] == 8.5);

    assert(dvec2.size() == 8);
    assert(dvec2[0] == 0.998);
    assert(dvec2[1] == 0.3456);
    assert(dvec2[4] == 0.00345);
    assert(dvec2[7] == 0.1);

    std::cout << "\nTesting sort 1 ..." << std::endl;

    df.sort<MyDataFrame::IndexType, int, double, std::string>
        (DF_INDEX_COL_NAME, sort_spec::ascen);
    dvec = df.get_column<double> ("dbl_col");
    dvec2 = df.get_column<double> ("dbl_col_2");

    assert(dvec.size() == 8);
    assert(dvec[0] == 1.2345);
    assert(dvec[1] == 2.2345);
    assert(dvec[3] == 4.2345);
    assert(dvec[5] == 8.5);
    assert(dvec[7] == 6.5);

    assert(dvec2.size() == 8);
    assert(dvec2[0] == 0.998);
    assert(dvec2[1] == 0.3456);
    assert(dvec2[4] == 0.00345);
    assert(dvec2[5] == 0.1);
    assert(dvec2[7] == 0.923);

    std::cout << "\nTesting sort 2 ..." << std::endl;

    df.sort<double, int, double, std::string>("dbl_col_2", sort_spec::desce);
    dvec = df.get_column<double> ("dbl_col");
    dvec2 = df.get_column<double> ("dbl_col_2");

    assert(dvec[0] == 1.2345);
    assert(dvec[7] == 5.2345);

    assert(dvec2[0] == 0.998);
    assert(dvec2[7] == 0.00345);

    std::cout << "\nTesting sort 3 ..." << std::endl;

    df.sort<double, int, double, std::string>("dbl_col_2", sort_spec::ascen);
    dvec = df.get_column<double> ("dbl_col");
    dvec2 = df.get_column<double> ("dbl_col_2");

    assert(dvec.size() == 8);
    assert(dvec[0] == 5.2345);
    assert(dvec[1] == 3.2345);
    assert(dvec[3] == 8.5);
    assert(dvec[5] == 2.2345);
    assert(dvec[7] == 1.2345);

    assert(dvec2.size() == 8);
    assert(dvec2[0] == 0.00345);
    assert(dvec2[1] == 0.056);
    assert(dvec2[4] == 0.15678);
    assert(dvec2[5] == 0.3456);
    assert(dvec2[7] == 0.998);

    std::cout << "\nTesting get_data_by_idx() ..." << std::endl;

    df.sort<MyDataFrame::IndexType, int, double, std::string>
        (DF_INDEX_COL_NAME, sort_spec::ascen);

    MyDataFrame df2 =
        df.get_data_by_idx<int, double, std::string>(
            Index2D<MyDataFrame::IndexType> { 3, 5 });

    dvec = df2.get_column<double> ("dbl_col");
    dvec2 = df2.get_column<double> ("dbl_col_2");

    assert(dvec.size() == 3);
    assert(dvec[0] == 3.2345);
    assert(dvec[1] == 4.2345);

    assert(dvec2.size() == 3);
    assert(dvec2[0] == 0.056);
    assert(dvec2[1] == 0.15678);

    std::cout << "\nTesting get_data_by_loc() ..." << std::endl;

    df.sort<double, int, double, std::string>("dbl_col_2", sort_spec::ascen);

    MyDataFrame df3 = df.get_data_by_loc<int, double, std::string>
        (Index2D<long> { 1, 2 });

    assert(df3.get_index().size() == 1);
    assert(df3.get_column<int>("int_col").size() == 1);
    assert(df3.get_column<double>("dbl_col").size() == 1);
    assert(df3.get_column<double>("dbl_col_2").size() == 1);
    assert(df3.get_column<std::string>("str_col").size() == 1);
    assert(df3.get_index()[0] == 3);
    assert(df3.get_column<double>("dbl_col")[0] == 3.2345);
    assert(df3.get_column<int>("col_name")[0] == 0);
    assert(df3.get_column<std::string>("str_col")[0] == "Col_name");

    // Printing the second df after get_data_by_loc() ...

    dvec = df3.get_column<double> ("dbl_col");
    dvec2 = df3.get_column<double> ("dbl_col_2");

    assert(dvec.size() == 1);
    assert(dvec[0] == 3.2345);

    assert(dvec2.size() == 1);
    assert(dvec2[0] == 0.056);

    std::cout << "\nTesting Correlation Visitor ..." << std::endl;

    CorrVisitor<double> corr_visitor;
    auto                fut10 =
        df.visit_async<double, double>("dbl_col", "dbl_col_2", corr_visitor);
    const double        corr = fut10.get().get_result();

    assert(fabs(corr - -0.358381) < 0.000001);

    std::cout << "\nTesting Stats Visitor ..." << std::endl;

    StatsVisitor<double>    stats_visitor;

    df.visit<double>("dbl_col", stats_visitor);
    dvec = df.get_column<double> ("dbl_col");
    assert(fabs(stats_visitor.get_skew() - 0.0396307) < 0.0001);
    assert(fabs(stats_visitor.get_kurtosis() - -1.273) < 0.0001);
    assert(fabs(stats_visitor.get_mean() - 4.83406) < 0.0001);
    assert(fabs(stats_visitor.get_variance() - 6.58781) < 0.0001);

    std::cout << "\nTesting SLRegression Visitor ..." << std::endl;

    SLRegressionVisitor<double> slr_visitor;

    df.visit<double, double>("dbl_col", "dbl_col_2", slr_visitor);
    assert(slr_visitor.get_count() == 8);
    assert(fabs(slr_visitor.get_slope() - -0.0561415) < 0.00001);
    assert(fabs(slr_visitor.get_intercept() - 0.602674) < 0.00001);
    assert(fabs(slr_visitor.get_corr() - -0.358381) < 0.00001);
    assert(fabs(df.visit<double, double>("dbl_col", "dbl_col_2",
                                        corr_visitor).get_result() -
               -0.358381) < 0.00001);

    std::cout << "\nTesting GROUPBY ..." << std::endl;

    std::vector<unsigned long>  ulgvec2 =
        { 123450, 123451, 123452, 123450, 123455, 123450, 123449,
          123448, 123451, 123452, 123452, 123450, 123455, 123450,
          123454, 123453, 123456, 123457, 123458, 123459, 123460,
          123441, 123442, 123432, 123433, 123434, 123435, 123436 };
    std::vector<unsigned long>  xulgvec2 = ulgvec2;
    std::vector<int>            intvec2 =
        { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
          15, 20, 22, 23, 24, 25, 30, 33, 34, 35, 36, 40, 45, 46 };
    std::vector<double>         xdblvec2 =
        { 1.2345, 2.2345, 3.2345, 4.2345, 5.2345, 3.0, 0.9999,
          10.0, 4.25, 0.009, 1.111, 8.0, 2.2222, 3.3333,
          11.0, 5.25, 1.009, 2.111, 9.0, 3.2222, 4.3333,
          12.0, 6.25, 2.009, 3.111, 10.0, 4.2222, 5.3333 };
    std::vector<double>         dblvec22 =
        { 0.998, 0.3456, 0.056, 0.15678, 0.00345, 0.923, 0.06743,
          0.1, 0.0056, 0.07865, -0.9999, 0.0111, 0.1002, -0.8888,
          0.14, 0.0456, 0.078654, -0.8999, 0.01119, 0.8002, -0.9888,
          0.2, 0.1056, 0.87865, -0.6999, 0.4111, 0.1902, -0.4888 };
    std::vector<std::string>    strvec2 =
        { "4% of something", "Description 4/5", "This is bad",
          "3.4% of GDP", "Market drops", "Market pulls back",
          "$15 increase", "Running fast", "C++14 development",
          "Some explanation", "More strings", "Bonds vs. Equities",
          "Almost done", "Here comes the sun", "XXXX1", "XXXX04",
          "XXXX2", "XXXX3", "XXXX4", "XXXX4", "XXXX5", "XXXX6",
          "XXXX7", "XXXX10", "XXXX11", "XXXX01", "XXXX02", "XXXX03" };

    MyDataFrame dfx;

    dfx.load_data(std::move(ulgvec2),
                  std::make_pair("xint_col", intvec2),
                  std::make_pair("dbl_col", xdblvec2),
                  std::make_pair("dbl_col_2", dblvec22),
                  std::make_pair("str_col", strvec2),
                  std::make_pair("ul_col", xulgvec2));
    dfx.write<std::ostream,
              int,
              unsigned long,
              double,
              std::string>(std::cout);

    const MyDataFrame   dfxx =
        dfx.groupby<GroupbySum,
                    unsigned long,
                    int,
                    unsigned long,
                    std::string,
                    double>(GroupbySum(), DF_INDEX_COL_NAME);

    dfxx.write<std::ostream,
               int,
               unsigned long,
               double,
               std::string>(std::cout);

    const MyDataFrame   dfxx2 =
        dfx.groupby<GroupbySum,
                    std::string,
                    int,
                    unsigned long,
                    std::string,
                    double>(GroupbySum(), "str_col");

    dfxx2.write<std::ostream,
                int,
                unsigned long,
                double,
                std::string>(std::cout);

    std::future<MyDataFrame>    gb_fut =
        dfx.groupby_async<GroupbySum,
                          double,
                          int,
                          unsigned long,
                          std::string,
                          double>(GroupbySum(), "dbl_col_2");
    const MyDataFrame           dfxx3 = gb_fut.get();

    dfxx3.write<std::ostream,
                int,
                unsigned long,
                double,
                std::string>(std::cout);

    std::cout << "\nTesting Async write ..." << std::endl;

    std::future<bool>   fut2 =
        dfxx3.write_async<std::ostream,
                          int,
                          unsigned long,
                          double,
                          std::string>(std::cout);

    fut2.get();

    std::cout << "\nTesting Async sort ..." << std::endl;

    auto    sf = dfx.sort_async<MyDataFrame::IndexType, std::string,
                                int, double, std::string, unsigned int>
                     (DF_INDEX_COL_NAME, sort_spec::ascen,
                      "str_col", sort_spec::desce);

    sf.get();

    std::cout << "\nTesting Async sort 2 ..." << std::endl;

    std::future<void>   sort_fut =
        dfx.sort_async<MyDataFrame::IndexType,
                       int, double, std::string, unsigned int>
            (DF_INDEX_COL_NAME, sort_spec::ascen);

    sort_fut.get();
    dfx.write<std::ostream,
              int,
              unsigned long,
              double,
              std::string>(std::cout);

    std::cout << "\nTesting Bucketize() ..." << std::endl;

    const MyDataFrame::IndexType    interval = 4;
    std::future<MyDataFrame>        b_fut =
        dfx.bucketize_async<GroupbySum,
                            int,
                            unsigned long,
                            std::string,
                            double>(GroupbySum(), interval);
    const MyDataFrame               buck_df = b_fut.get();

    buck_df.write<std::ostream,
                  int,
                  unsigned long,
                  double,
                  std::string>(std::cout);

    std::cout << "\nTesting multi_visit() ..." << std::endl;

    MeanVisitor<int>            ivisitor2;
    MeanVisitor<unsigned long>  ulvisitor;
    MeanVisitor<double>         dvisitor2;
    MeanVisitor<double>         dvisitor22;

    dfx.multi_visit(std::make_pair("xint_col", &ivisitor2),
                    std::make_pair("dbl_col", &dvisitor2),
                    std::make_pair("dbl_col_2", &dvisitor22),
                    std::make_pair("ul_col", &ulvisitor));
    assert(ivisitor2.get_result() == 19);
    assert(fabs(dvisitor2.get_result() - 4.5696) < 0.0001);
    assert(fabs(dvisitor22.get_result() - 0.0264609) < 0.00001);
    assert(ulvisitor.get_result() == 123448);

    const MyDataFrame   dfx_c = dfx;

    dfx_c.multi_visit(std::make_pair("xint_col", &ivisitor2),
                      std::make_pair("dbl_col", &dvisitor2),
                      std::make_pair("dbl_col_2", &dvisitor22),
                      std::make_pair("ul_col", &ulvisitor));
    assert(ivisitor2.get_result() == 19);
    assert(fabs(dvisitor2.get_result() - 4.5696) < 0.0001);
    assert(fabs(dvisitor22.get_result() - 0.0264609) < 0.00001);
    assert(ulvisitor.get_result() == 123448);

    MyDataFrame df_copy_con = dfx;

    assert((df_copy_con.is_equal<int,
                                 unsigned long,
                                 double,
                                 std::string>(dfx)));
    assert((! df_copy_con.is_equal<int,
                                   unsigned long,
                                   double,
                                   std::string>(dfxx)));

    df_copy_con.get_column<double>("dbl_col")[7] = 88.888888;
    assert(dfx.get_column<double>("dbl_col")[7] == 10.0);
    assert(
       fabs(df_copy_con.get_column<double>("dbl_col")[7] - 88.888888) <
                0.00001);
    assert(! (df_copy_con.is_equal<int,
                                   unsigned long,
                                   double,
                                   std::string>(dfx)));

    std::cout << "dfx before modify_by_idx()" << std::endl;
    dfx.write<std::ostream,
              int,
              unsigned long,
              double,
              std::string>(std::cout);

    dfx.modify_by_idx<int, unsigned long, double, std::string>(df_copy_con);
    std::cout << "dfx after modify_by_idx()" << std::endl;
    dfx.write<std::ostream,
              int,
              unsigned long,
              double,
              std::string>(std::cout);
    dfx.modify_by_idx<int, unsigned long, double, std::string>(df);
    std::cout << "dfx after modify_by_idx()" << std::endl;
    dfx.write<std::ostream,
              int,
              unsigned long,
              double,
              std::string>(std::cout);

    MyDataFrame::set_thread_level(5);
    assert(MyDataFrame::get_thread_level() == 5);
    MyDataFrame::set_thread_level(0);
    assert(MyDataFrame::get_thread_level() == 0);
    MyDataFrame::set_thread_level(10);
}

// -----------------------------------------------------------------------------

int main(int argc, char *argv[]) {

    test_haphazard();

    return (0);
}

// -----------------------------------------------------------------------------
