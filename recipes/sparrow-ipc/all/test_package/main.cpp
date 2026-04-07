/**
 * @file deserializer_example.cpp
 * @brief Examples demonstrating deserialization of Arrow IPC streams using sparrow-ipc
 *
 * This file shows different ways to deserialize Arrow IPC streams:
 * 1. Using the function API (deserialize_stream)
 * 2. Using the deserializer class for incremental deserialization
 */

#include <iostream>
#include <span>
#include <vector>

#include <sparrow/record_batch.hpp>

#include <sparrow_ipc/deserialize.hpp>
#include <sparrow_ipc/deserializer.hpp>
#include <sparrow_ipc/memory_output_stream.hpp>
#include <sparrow_ipc/serializer.hpp>

namespace sp = sparrow;
namespace sp_ipc = sparrow_ipc;

/**
 * Helper function to create sample record batches for demonstration
 */
std::vector<sp::record_batch> create_sample_batches(size_t count)
{
    std::vector<sp::record_batch> batches;
    for (size_t i = 0; i < count; ++i)
    {
        auto int_array = sp::primitive_array<int32_t>(
            {static_cast<int32_t>(i * 10), static_cast<int32_t>(i * 10 + 1), static_cast<int32_t>(i * 10 + 2)}
        );
        auto string_array = sp::string_array(std::vector<std::string>{
            "batch_" + std::to_string(i) + "_a",
            "batch_" + std::to_string(i) + "_b",
            "batch_" + std::to_string(i) + "_c"
        });
        batches.push_back(sp::record_batch(
            {{"id", sp::array(std::move(int_array))}, {"name", sp::array(std::move(string_array))}}
        ));
    }
    return batches;
}

/**
 * Helper function to serialize batches to a byte buffer
 */
std::vector<uint8_t> serialize_batches(const std::vector<sp::record_batch>& batches)
{
    std::vector<uint8_t> buffer;
    sp_ipc::memory_output_stream stream(buffer);
    sp_ipc::serializer ser(stream);
    ser << batches << sp_ipc::end_stream;
    return buffer;
}

// [example_deserialize_stream]
/**
 * Example: Deserialize a stream using the function API
 *
 * This is the simplest way to deserialize an Arrow IPC stream.
 * Use this when you have the complete stream data available.
 */
std::vector<sp::record_batch> deserialize_stream_example(const std::vector<uint8_t>& stream_data)
{
    // Deserialize the entire stream at once
    auto batches = sp_ipc::deserialize_stream(stream_data);
    return batches;
}

// [example_deserialize_stream]

// [example_deserializer_basic]
/**
 * Example: Basic usage of the deserializer class
 *
 * The deserializer class allows you to accumulate record batches
 * into an existing container as you deserialize data.
 */
void deserializer_basic_example(const std::vector<uint8_t>& stream_data)
{
    // Create a container to hold the deserialized batches
    std::vector<sp::record_batch> batches;

    // Create a deserializer that will append to our container
    sp_ipc::deserializer deser(batches);

    // Deserialize the stream data
    deser.deserialize(std::span<const uint8_t>(stream_data));

    // Process the accumulated batches
    for (const auto& batch : batches)
    {
        std::cout << "Batch with " << batch.nb_rows() << " rows and " << batch.nb_columns() << " columns\n";
    }
}

// [example_deserializer_basic]

// [example_deserializer_incremental]
/**
 * Example: Incremental deserialization with the deserializer class
 *
 * This example shows how to deserialize data incrementally as it arrives,
 * which is useful for streaming scenarios where data comes in chunks.
 */
void deserializer_incremental_example(const std::vector<std::vector<uint8_t>>& stream_chunks)
{
    // Container to accumulate all deserialized batches
    std::vector<sp::record_batch> batches;

    // Create a deserializer
    sp_ipc::deserializer deser(batches);

    // Deserialize chunks as they arrive using the streaming operator
    for (const auto& chunk : stream_chunks)
    {
        deser << std::span<const uint8_t>(chunk);
        std::cout << "After chunk: " << batches.size() << " batches accumulated\n";
    }

    // All batches are now available in the container
    std::cout << "Total batches deserialized: " << batches.size() << "\n";
}

// [example_deserializer_incremental]

// [example_deserializer_chaining]
/**
 * Example: Chaining multiple deserializations
 *
 * The streaming operator can be chained for fluent API usage.
 */
void deserializer_chaining_example(
    const std::vector<uint8_t>& chunk1,
    const std::vector<uint8_t>& chunk2,
    const std::vector<uint8_t>& chunk3
)
{
    std::vector<sp::record_batch> batches;
    sp_ipc::deserializer deser(batches);

    // Chain multiple deserializations in a single expression
    deser << std::span<const uint8_t>(chunk1) << std::span<const uint8_t>(chunk2)
          << std::span<const uint8_t>(chunk3);

    std::cout << "Deserialized " << batches.size() << " batches from 3 chunks\n";
}

// [example_deserializer_chaining]

int main()
{
    std::cout << "=== Sparrow IPC Deserializer Examples ===\n\n";

    try
    {
        // Create sample data
        auto original_batches = create_sample_batches(3);
        auto stream_data = serialize_batches(original_batches);

        std::cout << "1. Function API Example (deserialize_stream)\n";
        std::cout << "   ----------------------------------------\n";
        auto deserialized = deserialize_stream_example(stream_data);
        std::cout << "   Deserialized " << deserialized.size() << " batches\n\n";

        std::cout << "2. Basic Deserializer Class Example\n";
        std::cout << "   ---------------------------------\n";
        deserializer_basic_example(stream_data);
        std::cout << "\n";

        std::cout << "3. Incremental Deserialization Example\n";
        std::cout << "   ------------------------------------\n";
        // Create multiple chunks (each containing different batches)
        std::vector<std::vector<uint8_t>> chunks;
        for (size_t i = 0; i < 3; ++i)
        {
            auto batch = create_sample_batches(1);
            chunks.push_back(serialize_batches(batch));
        }
        deserializer_incremental_example(chunks);
        std::cout << "\n";

        std::cout << "4. Chaining Example\n";
        std::cout << "   -----------------\n";
        deserializer_chaining_example(chunks[0], chunks[1], chunks[2]);

        std::cout << "\n=== All examples completed successfully! ===\n";
    }
    catch (const std::exception& e)
    {
        std::cerr << "Error: " << e.what() << "\n";
        return 1;
    }

    return 0;
}
