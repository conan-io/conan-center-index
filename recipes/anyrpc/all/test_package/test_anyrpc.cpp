#include <cstdlib>
#include <iostream>

#include "anyrpc/anyrpc.h"

void testFunc(anyrpc::Value& params, anyrpc::Value& result)
{
}

int main(void)
{
    anyrpc::JsonHttpServer server;
    anyrpc::MethodManager* methodManager = server.GetMethodManager();
    methodManager->AddFunction(&testFunc, "testFunc", "Test function");

    return EXIT_SUCCESS;
}
