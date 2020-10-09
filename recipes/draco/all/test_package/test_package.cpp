#include <draco/compression/encode.h>

#include <cmath>
#include <iostream>
#include <memory>
#include <vector>

struct Vec3D {
  float x, y, z;
  Vec3D(float x, float y, float z): x(x), y(y), z(z) {}
};

struct Triangle {
  uint32_t i1, i2, i3;
  Triangle(uint32_t i1, uint32_t i2, uint32_t i3): i1(i1), i2(i2), i3(i3) {}
};

struct IndexedMesh {
  std::vector<Vec3D> vertices;
  std::vector<Triangle> primitives;

  unsigned long long size() {
    return vertices.size() * sizeof(Vec3D) + primitives.size() * sizeof(Triangle);
  }
};

std::vector<Vec3D> create_icosahedron_vertices() {
  std::vector<Vec3D> vertices;
  vertices.reserve(12);

  const float t = (1.0f + std::sqrt(5.0f)) / 2.0f;

  vertices.emplace_back(-1.0f,  t, 0.0f);
  vertices.emplace_back( 1.0f,  t, 0.0f);
  vertices.emplace_back(-1.0f, -t, 0.0f);
  vertices.emplace_back( 1.0f, -t, 0.0f);

  vertices.emplace_back(0.0f, -1.0f,  t);
  vertices.emplace_back(0.0f,  1.0f,  t);
  vertices.emplace_back(0.0f, -1.0f, -t);
  vertices.emplace_back(0.0f,  1.0f, -t);

  vertices.emplace_back( t, 0.0f, -1.0f);
  vertices.emplace_back( t, 0.0f,  1.0f);
  vertices.emplace_back(-t, 0.0f, -1.0f);
  vertices.emplace_back(-t, 0.0f,  1.0f);

  return vertices;
}

std::vector<Triangle> create_icosahedron_primitives() {
  std::vector<Triangle> primitives;
  primitives.reserve(20);

  primitives.emplace_back(0 , 11, 5 );
  primitives.emplace_back(0 , 5 , 1 );
  primitives.emplace_back(0 , 1 , 7 );
  primitives.emplace_back(0 , 7 , 10);
  primitives.emplace_back(0 , 10, 11);

  primitives.emplace_back(1 , 5 , 9 );
  primitives.emplace_back(5 , 11, 4 );
  primitives.emplace_back(11, 1 , 2 );
  primitives.emplace_back(10, 7 , 6 );
  primitives.emplace_back(7 , 1 , 8 );

  primitives.emplace_back(3 , 9 , 4 );
  primitives.emplace_back(3 , 4 , 2 );
  primitives.emplace_back(3 , 2 , 6 );
  primitives.emplace_back(3 , 6 , 8 );
  primitives.emplace_back(3 , 8 , 9 );

  primitives.emplace_back(4 , 9 , 5 );
  primitives.emplace_back(2 , 4 , 11);
  primitives.emplace_back(6 , 2 , 10);
  primitives.emplace_back(8 , 6 , 7 );
  primitives.emplace_back(9 , 8 , 1 );

  return primitives;
}

int main(int argc, char **argv) {
  // Create initial Mesh
  IndexedMesh mesh;
  mesh.vertices = create_icosahedron_vertices();
  mesh.primitives = create_icosahedron_primitives();

  // Create Draco Mesh from initial Mesh
  std::unique_ptr<draco::Mesh> dracoMesh(new draco::Mesh());
  dracoMesh->set_num_points(static_cast<uint32_t>(mesh.vertices.size()));

  draco::GeometryAttribute pos_attr;
  pos_attr.Init(draco::GeometryAttribute::POSITION, nullptr, 3, draco::DT_FLOAT32, false, sizeof(Vec3D), 0);
  const uint32_t pos_att_id = dracoMesh->AddAttribute(pos_attr, true, static_cast<uint32_t>(mesh.vertices.size()));
  for (std::size_t i = 0; i < mesh.vertices.size(); ++i) {
    dracoMesh->attribute(pos_att_id)->SetAttributeValue(
      draco::AttributeValueIndex(static_cast<uint32_t>(i)),
      &mesh.vertices[i]
    );
  }

  for (const auto &primitive : mesh.primitives) {
    dracoMesh->AddFace({
      draco::PointIndex(primitive.i1),
      draco::PointIndex(primitive.i2),
      draco::PointIndex(primitive.i3)
    });
  }

  std::cout << "Number of faces   : " << dracoMesh->num_faces() << "\n";
  std::cout << "Number of vertices: " << dracoMesh->num_points() << "\n";

  // Encode mesh with position's quantization of 16 bits and edgebreaker
  draco::Encoder encoder;
  encoder.SetAttributeQuantization(draco::GeometryAttribute::POSITION, 16);
  encoder.SetEncodingMethod(draco::MESH_EDGEBREAKER_ENCODING);
  draco::EncoderBuffer buffer;
  encoder.EncodeMeshToBuffer(*dracoMesh, &buffer);

  std::cout << "Initial mesh in " << mesh.size() << " bytes\n";
  std::cout << "Encoded mesh in " << buffer.size() << " bytes\n";

  return 0;
}
