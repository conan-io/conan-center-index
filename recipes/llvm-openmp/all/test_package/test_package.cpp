#include <omp.h>
#include <iostream>

#define THREAD_NUM 4

int main()
{
    omp_set_num_threads(THREAD_NUM);
    int actual_number;
    #pragma omp parallel
    {
        if(omp_get_thread_num() == 0){
            actual_number = omp_get_num_threads();
        }
    }
    if(actual_number != THREAD_NUM){
        std::cout << "Something went wrong. Expecting " << THREAD_NUM << " threads but found " << actual_number << ".\n";
        std::cout << "There are probably missing compiler flags.\n" ;
        return 1;
    }
    return 0;
}
