#include <iostream>
#include <vector>
#include <sparrow/record_batch.hpp>
#include <sparrow_ipc/deserialize.hpp>
#include <sparrow_ipc/memory_output_stream.hpp>
#include <sparrow_ipc/serializer.hpp>

int main() {
    namespace sp = sparrow;
    namespace ipc = sparrow_ipc;
    sp::record_batch batch({{"id", sp::array(sp::primitive_array<int32_t>({1, 2, 3}))}});
    std::vector<uint8_t> buffer;
    ipc::memory_output_stream stream(buffer);
    ipc::serializer ser(stream);
    ser << std::vector<sp::record_batch>{batch} << ipc::end_stream;
    auto batches = ipc::deserialize_stream(buffer);
    std::cout << "Round-tripped " << batches.size() << " batch(es)\n";
    return batches.size() == 1 ? 0 : 1;
}
