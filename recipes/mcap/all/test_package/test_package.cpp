#define MCAP_IMPLEMENTATION
#include <mcap/reader.hpp>
#include <mcap/writer.hpp>

#include <algorithm>
#include <chrono>

struct Buffer : mcap::IReadable, mcap::IWritable {
  std::vector<std::byte> buffer;

  virtual uint64_t size() const {
    return buffer.size();
  }

  // IWritable
  virtual void end() {}
  virtual void handleWrite(const std::byte* data, uint64_t size) {
    buffer.insert(buffer.end(), data, data + size);
  }

  // IReadable
  virtual uint64_t read(std::byte** output, uint64_t offset, uint64_t size) {
    if (offset + size > buffer.size()) {
      return 0;
    }
    *output = buffer.data() + offset;
    return size;
  }
};

void assertOk(const mcap::Status& status) {
  if (!status.ok()) {
    throw std::runtime_error(status.message);
  }
}

void expect(bool condition, const std::string& message) {
  if (!condition) {
    throw std::runtime_error(message);
  }
}

int main() {
  Buffer buffer;
  mcap::McapWriter writer;

  auto options = mcap::McapWriterOptions("example");
  options.compression = mcap::Compression::Zstd;

  writer.open(buffer, options);

  mcap::Schema schema("Example", "jsonschema",
                      R"({ "type": "object", "properties": { "foo": { "type": "string" } } })");
  writer.addSchema(schema);

  mcap::Channel channel("example", "json", schema.id);
  writer.addChannel(channel);

  auto now = std::chrono::duration_cast<std::chrono::nanoseconds>(
               std::chrono::system_clock::now().time_since_epoch())
               .count();

  std::string payload = R"({"foo": "bar"})";
  mcap::Message msg;
  msg.channelId = channel.id;
  msg.sequence = 0;
  msg.publishTime = now;
  msg.logTime = msg.publishTime;
  msg.data = reinterpret_cast<const std::byte*>(payload.data());
  msg.dataSize = payload.size();
  assertOk(writer.write(msg));

  writer.close();

  mcap::McapReader reader;
  assertOk(reader.open(buffer));
  assertOk(reader.readSummary(mcap::ReadSummaryMethod::NoFallbackScan, assertOk));
  expect(reader.statistics().value().schemaCount == 1, "incorrect schemaCount");
  expect(reader.statistics().value().channelCount == 1, "incorrect channelCount");
  expect(reader.statistics().value().messageCount == 1, "incorrect messageCount");
  expect(reader.statistics().value().chunkCount == 1, "incorrect chunkCount");
  for (const auto& msgView : reader.readMessages()) {
    expect(msgView.channel->id == channel.id, "incorrect channel id");
    expect(msgView.channel->topic == channel.topic, "incorrect channel topic");
    expect(msgView.channel->messageEncoding == channel.messageEncoding,
           "incorrect channel messageEncoding");
    expect(msgView.schema->id == schema.id, "incorrect schema id");
    expect(msgView.schema->name == schema.name, "incorrect schema name");
    expect(msgView.schema->encoding == schema.encoding, "incorrect schema encoding");
    expect(msgView.message.sequence == msg.sequence, "incorrect message sequence");
    expect(msgView.message.logTime == msg.logTime, "incorrect message logTime");
    expect(msgView.message.publishTime == msg.publishTime, "incorrect message publishTime");
    expect(msgView.message.dataSize == msg.dataSize, "incorrect message dataSize");
    expect(msgView.message.data != msg.data, "data should be copied");
    expect(std::equal(msgView.message.data, msgView.message.data + msgView.message.dataSize,
                      msg.data, msg.data + msg.dataSize),
           "incorrect data");
  }
  std::cout << "MCAP " << mcap::LibraryVersion << " roundtrip succeeded!" << std::endl;
  return 0;
}
