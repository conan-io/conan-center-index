#include <boost/stacktrace.hpp>

int main() {
    boost::stacktrace::stacktrace st;
    st.size();
    return 0;
}
