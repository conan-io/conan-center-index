#include <iostream>

extern "C"
{
    int yyerror(char *);
}

int main()
{
    char error[] = "Bincrafters";
    std::cout << yyerror(error) << std::endl;
    return 0;
}
