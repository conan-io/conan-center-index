#include <iostream>
#include <Corrade/PluginManager/Manager.h>
#include <Magnum/Trade/AbstractImporter.h>

#include "configure.h"

int main() {
    Corrade::PluginManager::Manager<Magnum::Trade::AbstractImporter> manager{IMPORTER_PLUGINS_FOLDER};
    manager.load("StlImporter");
    auto importer = manager.instantiate("StlImporter");

    if(!importer) Magnum::Fatal{} << "Cannot load the StlImporter plugin";

    importer->openFile(CONAN_STL_FILE);
    std::cout << "Mesh count: " << importer->meshCount() << "\n";
    return 0;
}
