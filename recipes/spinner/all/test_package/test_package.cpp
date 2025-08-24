#include <iostream>
#include<spinner.h>
#include<thread>
#include<chrono>

void leafApp()
{
    Spinner spinner("Launching leaf app..");
    spinner.start();
    std::this_thread::sleep_for(std::chrono::seconds(5));
    spinner.stop();
    std::cout<<"Done!\n";
}