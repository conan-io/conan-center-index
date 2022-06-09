#include <OGRE/Paging/OgrePaging.h>
#include <iostream>
#include <memory>

int main(int argc, char **argv) {
  std::unique_ptr<Ogre::Page> page{nullptr};
  std::cout << "Hello from Ogre::Overlay component\n";
  return 0;
}

