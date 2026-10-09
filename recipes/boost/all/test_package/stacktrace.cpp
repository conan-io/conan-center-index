#include <boost/stacktrace.hpp>

int main() {
    BOOST_NAMESPACE::stacktrace::stacktrace st;
    st.size();
    return 0;
}
