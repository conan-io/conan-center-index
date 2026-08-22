#include <plf_list.h>

int main() {
    int arr[] = {1, 2, 3, 4, 5};
    plf::list<int> list1(arr, arr + sizeof(arr) / sizeof(int));
    plf::list<int>::iterator it = --(list1.end());
    list1.splice(list1.begin(), it);
    return 0;
}
