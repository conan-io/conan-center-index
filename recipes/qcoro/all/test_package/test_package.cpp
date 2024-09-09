#include <qcorofuture.h>
#include <QtConcurrent>

QCoro::Task<> startTask() {
    const auto data = co_await QtConcurrent::run([]() {
        return 0;
    });
}

int main(int argc, char **argv) {
    return 0;
}
