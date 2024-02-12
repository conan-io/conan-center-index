#include <cstdlib>
#include <iostream>
#include "vtu11/vtu11.hpp"


int main(void) {
    // Create data for 3x2 quad mesh: (x, y, z) coordinates of mesh vertices
    std::vector<double> points
    {
        0.0, 0.0, 0.5,    0.0, 0.3, 0.5,    0.0, 0.7, 0.5,    0.0, 1.0, 0.5, // 0,  1,  2,  3
        0.5, 0.0, 0.5,    0.5, 0.3, 0.5,    0.5, 0.7, 0.5,    0.5, 1.0, 0.5, // 4,  5,  6,  7
        1.0, 0.0, 0.5,    1.0, 0.3, 0.5,    1.0, 0.7, 0.5,    1.0, 1.0, 0.5  // 8,  9, 10, 11
    };

    // Vertex indices of all cells
    std::vector<vtu11::VtkIndexType> connectivity
    {
        0,  4,  5,  1, // 0
        1,  5,  6,  2, // 1
        2,  6,  7,  3, // 2
        4,  8,  9,  5, // 3
        5,  9, 10,  6, // 4
        6, 10, 11,  7  // 5
    };

    // Separate cells in connectivity array
    std::vector<vtu11::VtkIndexType> offsets { 4, 8, 12, 16, 20, 24 };

    // Cell types of each cell, see [1]
    std::vector<vtu11::VtkCellType> types { 9, 9, 9, 9, 9, 9 };

    // Create small proxy mesh type
    vtu11::Vtu11UnstructuredMesh mesh { points, connectivity, offsets, types };

    // Create some data associated to points and cells
    std::vector<double> pointData { 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0 };
    std::vector<double> cellData { 3.2, 4.3, 5.4, 6.5, 7.6, 8.7 };

    // Create tuples with (name, association, number of components) for each data set
    std::vector<vtu11::DataSetInfo> dataSetInfo
    {
        vtu11::DataSetInfo{ "Temperature", vtu11::DataSetType::PointData, 1 },
        vtu11::DataSetInfo{ "Conductivity", vtu11::DataSetType::CellData, 1 },
    };

    // Write data to .vtu file using Ascii format
    vtu11::writeVtu( "test.vtu", mesh, dataSetInfo, { pointData, cellData }, "Ascii" );

    return EXIT_SUCCESS;
}
