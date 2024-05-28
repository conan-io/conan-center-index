#include <velodyne_decoder/config.h>
#include <velodyne_decoder/scan_decoder.h>
#include <velodyne_decoder/stream_decoder.h>
#include <velodyne_decoder/types.h>

int main() {
  velodyne_decoder::Config config;
  velodyne_decoder::StreamDecoder stream_decoder(config);
}
