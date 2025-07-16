#include <foxglove/foxglove.hpp>
#include <foxglove/mcap.hpp>
#include <foxglove/server.hpp>

#include <cassert>
#include <filesystem>
#include <fstream>

class FileCleanup
{
public:
    explicit FileCleanup(std::string &&path)
        : path_(std::move(path)) {}
    ~FileCleanup()
    {
        if (std::filesystem::exists(path_))
        {
            std::filesystem::remove(path_);
        }
    }

private:
    std::string path_;
};

int main(void)
{
    FileCleanup cleanup("foxglove-sdk-test.mcap");
    foxglove::WebSocketServerOptions unused_;
    foxglove::McapWriterOptions options;
    options.path = "foxglove-sdk-test.mcap";
    options.compression = foxglove::McapCompression::None;

    auto writer_result = foxglove::McapWriter::create(options);
    assert(writer_result.has_value());
    auto writer = std::move(writer_result.value());

    auto channel_result = foxglove::schemas::SceneUpdateChannel::create("/scene");
    assert(channel_result.has_value());

    auto scene_channel = std::move(channel_result.value());
    foxglove::schemas::SceneUpdate scene_update;
    scene_channel.log(scene_update);

    writer.close();

    std::ifstream file("foxglove-sdk-test.mcap", std::ios::binary);
    assert(file.is_open());
    std::string contents = {std::istreambuf_iterator<char>(file), std::istreambuf_iterator<char>()};
    assert(contents.find("SceneUpdate") != std::string::npos);

    return EXIT_SUCCESS;
}
