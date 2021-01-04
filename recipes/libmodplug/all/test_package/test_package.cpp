#include <iostream>
#include <cstdio>
#include <vector>
#include <libmodplug/modplug.h>

int main(int argc, char * const argv[])
{
    if (argc < 2)
        return -1;
    FILE * f = fopen(argv[1], "rb");
    if (!f)
        return -2;
    
    fseek(f, 0, SEEK_END);
    long fsize = ftell(f);
    fseek(f, 0, SEEK_SET);
    
    std::vector<unsigned char> b(fsize);
    fread(&b[0], fsize, 1, f);

    fclose(f);
    
    ModPlugFile * m = ModPlug_Load(&b[0], fsize);
    if (!m)
        return -3;
    
    std::cout << "name: " << ModPlug_GetName(m) << std::endl;
    std::cout << "length: " << ModPlug_GetLength(m) << " ms" << std::endl;
    
    ModPlug_Unload(m);
    return 0;
}
