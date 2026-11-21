#include <hakka_json_int.hpp>
#include <hakka_json_string.hpp>
#include <hakka_json_array.hpp>
#include <iostream>

using namespace hakka;

template <typename T>
T *h2t_mut(JsonHandleCompact &handle)
{
    auto mut_ptr = handle.get_mut_ptr();
    return std::get<T*>(mut_ptr);
}

int main() {
    auto int_val = JsonIntCompact::create(42);
    auto str_val = JsonStringCompact::create("Hello, Conan!");
    auto arr_val = JsonArrayCompact::create();

    h2t_mut<JsonArrayCompact>(arr_val)->push_back(int_val);
    h2t_mut<JsonArrayCompact>(arr_val)->push_back(str_val);

    std::cout << "Hakka JSON test package successful!" << std::endl;
    std::cout << "Array size: " << h2t_mut<JsonArrayCompact>(arr_val)->length() << std::endl;

    return 0;
}
