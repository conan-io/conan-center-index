#include <vector>
#include <iostream>
#include <cppcoro/generator.hpp>
#include <cppcoro/task.hpp>
#include <cppcoro/sync_wait.hpp>

cppcoro::generator<int> intYielder() {
	co_yield 0;
	co_yield 1;
}

cppcoro::task<int> task() {
    co_return 42;
}

int main() {
    auto _ = cppcoro::sync_wait(task());

	std::vector<int> v;
	for (int n : intYielder()) {
        std::cout << "yielded " << n << '\n';
		v.push_back(n);
	}

	bool success = v[0] == 0 && v[1] == 1;
    if (success) {
        std::cout << "success";
        return 0;
    } else {
        return 1;
    }
}
