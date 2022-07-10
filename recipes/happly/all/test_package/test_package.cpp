#include <happly.h>


int main(int argc, char const *argv[])
{
    // Suppose these hold your data
    std::vector<std::array<double, 3>> meshVertexPositions;
    std::vector<std::array<double, 3>> meshVertexColors;
    std::vector<std::vector<size_t>> meshFaceIndices;

    // Create an empty object
    happly::PLYData plyOut;

    // Add mesh data (elements are created automatically)
    plyOut.addVertexPositions(meshVertexPositions);
    plyOut.addVertexColors(meshVertexColors);
    plyOut.addFaceIndices(meshFaceIndices);


    // Write the object to file
    plyOut.write("my_output_mesh_file.ply", happly::DataFormat::ASCII);

    return 0;
}
