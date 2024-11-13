#include <IPhreeqc.h>

int main()
{
    int id = CreateIPhreeqc();
    DestroyIPhreeqc(id);
    return 0;
}
