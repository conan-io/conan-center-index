#include <mio/mmap.hpp>

#include <algorithm>
#include <cassert>
#include <cstdio>
#include <fstream>
#include <system_error>

int handle_error(const std::error_code &error) {
    const auto &errmsg = error.message();
    std::printf("error mapping file: %s, exiting...\n", errmsg.c_str());
    return error.value();
}

void allocate_file(const std::string &path, const int size) {
    std::ofstream file(path);
    std::string s(size, '0');
    file << s;
}

int main() {
    const auto path = "file.txt";
    allocate_file(path, 155);

    std::error_code error;
    mio::mmap_sink rw_mmap = mio::make_mmap_sink(path, 0, mio::map_entire_file, error);
    if (error) { return handle_error(error); }

    std::fill(rw_mmap.begin(), rw_mmap.end(), 'a');

    for (auto &b : rw_mmap) {
        b += 10;
    }

    const int answer_index = rw_mmap.size() / 2;
    rw_mmap[answer_index] = 42;

    rw_mmap.sync(error);
    if (error) { return handle_error(error); }

    rw_mmap.unmap();

    mio::mmap_source ro_mmap;
    ro_mmap.map(path, error);
    if (error) { return handle_error(error); }

    const int the_answer_to_everything = ro_mmap[answer_index];
    assert(the_answer_to_everything == 42);

    return 0;
}
