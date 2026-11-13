#include <cstdlib>

#include <COLLADASWStreamWriter.h>
#include <COLLADASWNode.h>
#include <COLLADASWLibraryGeometries.h>
#include <COLLADASWLibraryVisualScenes.h>
#include <COLLADASWLibraryEffects.h>
#include <COLLADASWLibraryMaterials.h>

// From cpp
#include <COLLADASWPrimitves.h>
#include <COLLADASWSource.h>
#include <COLLADASWScene.h>
#include <COLLADASWNode.h>
#include <COLLADASWInstanceGeometry.h>
#include <COLLADASWBaseInputElement.h>
#include <COLLADASWAsset.h>

int main(void) {

    COLLADASW::StreamWriter stream(COLLADASW::NativeString("test_output.dae", COLLADASW::NativeString::ENCODING_UTF8));
    stream.startDocument();
    // exporter.startDocument(unit_name, unit_magnitude);

    return EXIT_SUCCESS;
}
