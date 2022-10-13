#include <ntv2utils.h>
#include <ntv2card.h>

int main()
{
    std::cout << "hello AJA NTV2 version " << NTV2GetVersionString() << "\n";
    CNTV2Card card;
    std::cout << "card name is " << card.GetDisplayName() << '\n';
    return 0;
}
