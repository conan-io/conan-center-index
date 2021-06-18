#include <transwarp.h>

#include <fstream>
#include <iostream>

int main() {
    double x = 0;
    int y = 0;

    auto parent1 = transwarp::make_task(
        transwarp::root,
        [&x]() { return 13.3 + x; }
    )->named("something");
    auto parent2 = transwarp::make_task(
        transwarp::root,
        [&y]() { return 42 + y; }
    )->named("something else");
    auto child = transwarp::make_task(
        transwarp::consume,
        [](double a, int b) { return a + b; },
        parent1,
        parent2
    )->named("adder");

    transwarp::parallel executor{4};

    child->schedule_all(executor);
    std::cout << "result = " << child->get() << std::endl;

    x += 2.5;
    y += 1;

    child->schedule_all(executor);
    std::cout << "result = " << child->get() << std::endl;

    std::ofstream{"basic_with_three_tasks.dot"} << transwarp::to_string(child->edges());

    return 0;
}
