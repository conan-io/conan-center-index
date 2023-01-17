#include <iostream>

#include <wavelet_buffer/wavelet_buffer.h>

using drift::Signal1D;
using drift::WaveletBuffer;
using drift::WaveletParameters;
using drift::WaveletTypes;
using DenoiseAlgo = drift::ThresholdAbsDenoiseAlgorithm<float>;

int main() {
  Signal1D original = blaze::generate(
      1000, [](auto index) { return static_cast<float>(index % 100); });

  std::cout << "Original size: " << original.size() * 4 << std::endl;
  WaveletBuffer buffer(WaveletParameters{
      .signal_shape = {original.size()},
      .signal_number = 1,
      .decomposition_steps = 3,
      .wavelet_type = WaveletTypes::kDB1,
  });

  // Wavelet decomposition of the signal and denoising
  buffer.Decompose(original, DenoiseAlgo(0, 0.3));

  // Compress the buffer
  std::string arch;
  if (buffer.Serialize(&arch, 16)) {
    std::cout << "Compressed size: " << arch.size() << std::endl;
  } else {
    std::cerr << "Serialization error" << std::endl;
    return EXIT_FAILURE;
  }

  // Decompress the buffer
  auto restored_buffer = WaveletBuffer::Parse(arch);
  Signal1D output_signal;

  // Restore the signal from wavelet decomposition
  restored_buffer->Compose(&output_signal);

  std::cout << "Distance between original and restored signal: "
            << blaze::norm(original - output_signal) / original.size()
            << std::endl;
  std::cout << "Compression rate: " << original.size() * 4. / arch.size() * 100
            << "%" << std::endl;
}
