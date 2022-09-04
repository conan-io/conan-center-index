#pragma once

#include <stdio.h>


namespace ImGui
{
    void MyFunction(const char* name) {
        printf("  ImGui::MyFunction(%s)\n", name);
    }
}
