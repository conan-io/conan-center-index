#include <ittnotify.h>
#include <iostream>

// @note Domains cannot be destroyed.
__itt_domain* itt_domain = __itt_domain_create("Global Domain");

int main(){
    __itt_string_handle* nameHandle = __itt_string_handle_create("My name");
    __itt_task_begin(itt_domain, __itt_null, __itt_null, nameHandle);
    std::cout << "Inside ITT range." << std::endl;
    __itt_task_end(itt_domain);

    return 0;
}
