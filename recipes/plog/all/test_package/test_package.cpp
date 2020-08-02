#include <iostream>

#include <plog/Log.h>

int main() {
    plog::init(plog::debug, "log.txt");
    PLOG(plog::info) << "Hello world!";
    return 0;
}

