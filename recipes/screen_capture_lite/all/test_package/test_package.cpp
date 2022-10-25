#include <iostream>
#include "ScreenCapture.h"

int main() {
    SL::Screen_Capture::CreateCaptureConfiguration([](){
        return SL::Screen_Capture::GetMonitors();
    });
}
