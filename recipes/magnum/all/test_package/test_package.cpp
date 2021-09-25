#include <iostream>
#include "Magnum/Math/Vector.h"
#include "Magnum/Math/StrictWeakOrdering.h"
#include <Corrade/PluginManager/Manager.h>
#include <Magnum/Trade/AbstractImporter.h>

#include "configure.h"

/*
    I would like to use some windowless application to test, like
    https://github.com/mosra/magnum-bootstrap/tree/windowless
    but it doesn't work in CI, it complains about EGL_NOT_INITIALIZED
    (headless machine?)
*/

int main() {
    // Test some basic Magnum
    const Magnum::Math::Vector<2, Magnum::Float> v2a{1.0f, 2.0f};
    const Magnum::Math::Vector<2, Magnum::Float> v2b{2.0f, 3.0f};
    const Magnum::Math::Vector<2, Magnum::Float> v2c{1.0f, 3.0f};

    Magnum::Math::StrictWeakOrdering o;
    if (o(v2a, v2b)) {
        std::cout << "Basic Magnum working\n";
    }

    // Test some plugin
    Corrade::PluginManager::Manager<Magnum::Trade::AbstractImporter> manager{IMPORTER_PLUGINS_FOLDER};
    manager.load("ObjImporter");
    auto importer = manager.instantiate("ObjImporter");

    if(!importer) Magnum::Fatal{} << "Cannot load the ObjImporter plugin";

    importer->openFile(OBJ_FILE);
    std::cout << "Mesh count: " << importer->meshCount() << "\n";
    return 0;
}
