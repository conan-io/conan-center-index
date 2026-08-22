#include <cstdlib>

#include <MaterialXFormat/File.h>
#include <MaterialXCore/Document.h>
#include <MaterialXCore/Value.h>
#include <MaterialXFormat/XmlIo.h>
#include <MaterialXFormat/Util.h>

namespace mx = MaterialX;

int main(void) {

    mx::DocumentPtr doc = mx::createDocument();

    // Create a base shader nodedef.
    mx::NodeDefPtr simpleSrf = doc->addNodeDef("ND_simpleSrf", mx::SURFACE_SHADER_TYPE_STRING, "simpleSrf");
    simpleSrf->setInputValue("diffColor", mx::Color3(1.0f));
    simpleSrf->setInputValue("specColor", mx::Color3(0.0f));
    simpleSrf->setInputValue("roughness", 0.25f);
    simpleSrf->setTokenValue("texId", "01");

    // Create an inherited shader nodedef.
    mx::NodeDefPtr anisoSrf = doc->addNodeDef("ND_anisoSrf", mx::SURFACE_SHADER_TYPE_STRING, "anisoSrf");
    anisoSrf->setInheritsFrom(simpleSrf);
    anisoSrf->setInputValue("anisotropy", 0.0f);

    // Instantiate shader and material nodes.
    mx::NodePtr shaderNode = doc->addNode(anisoSrf->getNodeString(), "", anisoSrf->getType());
    mx::NodePtr materialNode = doc->addMaterialNode("", shaderNode);

    // Set nodedef and shader node qualifiers.
    shaderNode->setVersionString("2.0");
    anisoSrf->setVersionString("2");
    shaderNode->setVersionString("2");
    shaderNode->setType(mx::VOLUME_SHADER_TYPE_STRING);
    shaderNode->setType(mx::SURFACE_SHADER_TYPE_STRING);

    // Bind a shader input to a value.
    mx::InputPtr instanceSpecColor = shaderNode->setInputValue("specColor", mx::Color3(1.0f));

    return EXIT_SUCCESS;
}
