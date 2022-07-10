#include <iostream>

extern "C"
{
    int yyerror(const char *);
}

int main()
{
    char error[] = "conan-center-index";
    std::cout << yyerror(error) << std::endl;
    return 0;
}
