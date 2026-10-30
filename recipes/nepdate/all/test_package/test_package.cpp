#include <nepdate/nepdate.hpp>
#ifdef NEPDATE_TEST_PATRO
#include <nepdate/patro.hpp>
#endif

#include <cstdio>

int main() {
    const nepdate::date d = nepdate::make_date(2081, 4, 15).value();
    std::printf("%s\n", nepdate::to_string(d).c_str());
#ifdef NEPDATE_TEST_PATRO
    std::printf("events: %zu\n", nepdate::patro::info(d).events().size());
#endif
    return 0;
}
