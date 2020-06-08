#include <taskflow/taskflow.hpp>

int main()
{
    tf::Executor executor;
    tf::Taskflow taskflow;

    auto A = taskflow.emplace([](){ std::cout << "Task A\n"; });
    auto B = taskflow.emplace([](){ std::cout << "Task B\n"; });
    auto C = taskflow.emplace([](){ std::cout << "Task C\n"; });
    auto D = taskflow.emplace([](){ std::cout << "Task D\n"; });
                                            
                                               //                                 
                                               //          +---+                  
                                               //    +---->| B |-----+            
                                               //    |     +---+     |            
                                               //  +---+           +-v-+          
                                               //  | A |           | D |          
    A.precede(B);    // B runs after A         //  +---+           +-^-+          
    A.precede(C);    // C runs after A         //    |     +---+     |            
    B.precede(D);    // D runs after B         //    +---->| C |-----+            
    C.precede(D);    // D runs after C         //          +---+

    executor.run(taskflow).get();

    return 0;
}
