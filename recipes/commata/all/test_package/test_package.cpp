#include <iostream>
#include <vector>

#include "commata/parse_csv.hpp"

template <class Ch>
class test_collector
{
    std::vector<std::vector<std::basic_string<Ch>>>* field_values_;
    std::basic_string<Ch> field_value_;

public:
    using char_type = Ch;

    explicit test_collector(
        std::vector<std::vector<std::basic_string<Ch>>>& field_values) :
        field_values_(&field_values)
    {}

    void start_record(const Ch* /*record_begin*/)
    {
        field_values_->emplace_back();
    }

    void update(const Ch* first, const Ch* last)
    {
        field_value_.append(first, last);
    }

    void finalize(const Ch* first, const Ch* last)
    {
        field_value_.append(first, last);
        field_values_->back().emplace_back();
        field_values_->back().back().swap(field_value_);
            // field_value_ is cleared here
    }

    void end_record(const Ch* /*record_end*/)
    {}
};

int main(void) {
    std::string s = R"(,"col1", col2 ,col3,)" "\r\n"
                    "\n"
                    R"( cell10 ,,"cell)" "\r\n"
                    R"(12","cell""13""","")" "\n";

    std::stringbuf buf(s);

    std::vector<std::vector<std::string>> field_values;

    test_collector<char> collector(field_values);
#ifdef COMMATA_VERSION_LESS_0_2_7
    commata::parse_csv(&buf, collector);
#else
    commata::parse_csv(buf, collector);
#endif

    std::cout << field_values.size() << '\n';

    return 0;
}
