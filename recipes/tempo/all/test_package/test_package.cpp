#include <tempo/models/debouncer.tpp>

int main() {
    tempo::Debouncer<int> debouncer(
        [](auto _) {
        },
        std::chrono::milliseconds(10)
    );

    return 0;
}
