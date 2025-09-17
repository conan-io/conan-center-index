#include <iostream>
#include <vector>

#include <ppqsort.h>

void print_vector(const std::vector<int>& vec) {
    for (const auto& elem : vec)
        std::cout << elem << " ";
    std::cout << std::endl;
}

int main()
{
    std::vector<int> input = {5, 3, 8, 6, 2, 7, 4, 1};
    std::cout << "Original vector: ";
    print_vector(input);
    ppqsort::sort(ppqsort::execution::par, input.begin(), input.end());
    std::cout << "Sorted vector: ";
    print_vector(input);
    return 0;
}
