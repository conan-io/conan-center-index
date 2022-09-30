#include <snowhouse/snowhouse.h>
#include <bandit/bandit.h>

using namespace snowhouse;
using namespace bandit;

go_bandit([]() {
    describe("context", []() {
        bool b;

        before_each([&]() {
            b = true;
        });

        it("is true", [&]() {
            AssertThat(b, IsTrue());
        });
    });
});

int main(int argc, char** argv) {
    return bandit::run(argc, argv);
}

