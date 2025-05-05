#include "tbb/task_group.h"
#include "tbb/flow_graph.h"
#include <iostream>

using namespace tbb;
using namespace tbb::flow;

int Fib(int n) {
    if( n<2 ) {
        return n;
    } else {
        int x, y;
        task_group g;
        g.run([&]{x=Fib(n-1);}); // spawn a task
        g.run([&]{y=Fib(n-2);}); // spawn another task
        g.wait();                // wait for both tasks to complete
        return x+y;
    }
}

int main(){
    std::cout<<"Fib 6="<<Fib(6)<<"\n";

    graph g;
    continue_node< continue_msg> hello( g,
      []( const continue_msg &) {
          std::cout << "Hello";
      }
    );
    continue_node< continue_msg> world( g,
      []( const continue_msg &) {
          std::cout << " World\n";
      }
    );
    make_edge(hello, world);
    hello.try_put(continue_msg());
    g.wait_for_all();
    return 0;
}
