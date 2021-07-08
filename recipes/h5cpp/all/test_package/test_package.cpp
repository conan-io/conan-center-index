#include <h5cpp/hdf5.hpp>

using hdf5::file::AccessFlags;

int main() {
    auto f = hdf5::file::create("test.h5", AccessFlags::TRUNCATE);
    auto root = f.root();
    auto group = root.create_group("group");
    std::vector<int> data{1, 2, 3, 4};
    auto dataset = group.create_dataset(
        "data",
        hdf5::datatype::create<std::vector<int>>(),
        hdf5::dataspace::create(data)
    );

    dataset.write(data);

    return 0;
}
