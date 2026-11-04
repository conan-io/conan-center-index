#include "ctrl-c.h"

int main(void) {
    auto id = CtrlCLibrary::SetCtrlCHandler([](CtrlCLibrary::CtrlSignal signal){ return true;});
    CtrlCLibrary::ResetCtrlCHandler(id);

    return 0;
}
