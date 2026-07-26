#include <chronicle/chronicle.hpp>
#include <cstdio>

int main() {
    chronicle::Session session;
    chronicle::tracked<int> counter{0};
    chronicle::track(counter, session, "counter");

    chronicle::set(counter, 1);
    chronicle::set(counter, 2);
    chronicle::set(counter, 3);

    auto timeline = chronicle::history(counter);

    std::printf("final value: %d\n", static_cast<int>(counter));
    std::printf("history size: %zu\n", timeline.size());
    return (static_cast<int>(counter) == 3 && timeline.size() == 4) ? 0 : 1;
}
