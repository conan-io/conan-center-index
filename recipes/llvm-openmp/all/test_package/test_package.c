#include <omp.h>

#include <stdio.h>

int main()
{
    int num_threads = omp_get_num_procs();
    if (num_threads < 5)
        num_threads = 5;
    omp_set_num_threads(num_threads);
    int actual_number;
    #pragma omp parallel
    {
       #pragma omp single
       {
          actual_number = omp_get_num_threads();
       }
    }
    if(actual_number != num_threads){
        printf("Something went wrong. Expecting %d threads but found %d.\n", num_threads, actual_number);
        printf("There are probably missing compiler flags.\n");
        return 1;
    }
    return 0;
}
