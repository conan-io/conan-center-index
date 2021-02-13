#include <GLTFSDK/GLTF.h>
#include <GLTFSDK/Deserialize.h>
#include <GLTFSDK/Document.h>
#include <GLTFSDK/Math.h>
#include <GLTFSDK/Serialize.h>

#include <iostream>
#include <utility>

int main() {
  Microsoft::glTF::Document originalDoc;

  {
    Microsoft::glTF::Scene sc;
    sc.id = "0";
    sc.nodes = { "0" };
    originalDoc.SetDefaultScene(std::move(sc));
  }

  {
    Microsoft::glTF::Node matrixNode;
    matrixNode.id = "0";
    matrixNode.name = "matrixNode";
    matrixNode.matrix = Microsoft::glTF::Matrix4::IDENTITY;
    originalDoc.nodes.Append(std::move(matrixNode));
  }

  std::cout << Microsoft::glTF::Serialize(originalDoc) << std::endl;

  return 0;
}
