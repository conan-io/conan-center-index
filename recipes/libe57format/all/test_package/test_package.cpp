#include <E57Format/E57SimpleWriter.h>
#include <E57Format/E57SimpleData.h>
#include <E57Format/E57SimpleReader.h>
#include <E57Format/E57Exception.h>

int main() {
  e57::Writer writer("file.e57");
  e57::Image2D image_header;
  std::int64_t index = writer.NewImage2D(image_header);
  std::vector<std::uint8_t> image_bytes(100, 1);
  std::int64_t n_bytes = writer.WriteImage2DData(index, e57::E57_JPEG_IMAGE, e57::E57_NO_PROJECTION,
                                                 image_bytes.data(), 0, image_bytes.size());

  try {
    e57::Reader reader("invalid-file.e57");
  } catch (const e57::E57Exception& e) { }

  return 0;
}
