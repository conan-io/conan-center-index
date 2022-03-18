#include <iostream>

#include <ignition/plugin/Loader.hh>
#include <ignition/plugin/WeakPluginPtr.hh>

int main(int argc, char** argv)
{
  std::cout << "Hello from ignition plugin test package\n";
  ignition::plugin::Loader pl;
  ignition::plugin::WeakPluginPtr weak;

}
