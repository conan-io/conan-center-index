// Async example from https://stlab.cc/libraries/concurrency/

#include <iostream>
#include <thread>

#include <stlab/concurrency/default_executor.hpp>
#include <stlab/concurrency/future.hpp>

using namespace std;
using namespace stlab;

int main() {
    auto f = async(default_executor, [] { return 42; });

    // Waiting just for illustration purpose
    while (!f.get_try()) { this_thread::sleep_for(chrono::milliseconds(1)); }

    cout << "The answer is " << *f.get_try() << "\n";
}

/*
    Result:

        The answer is 42
*/
