#include <iostream>

#include <itlib/pod_vector.hpp>

struct my_pod
{
    int number;
};

int main()
{
    itlib::pod_vector<my_pod> vector;
    vector.insert(vector.begin(), { 10 });

    my_pod pod = vector[0];
    std::cout << "Number is " << pod.number << std::endl;
    return 0;
}
