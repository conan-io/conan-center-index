#include "sdl_painter/app/application.h"
#include "sdl_painter/pen.h"
#include "sdl_painter/renderer.h"
#include "sdl_painter/version.h"

#include <cstdio>
#include <cstdlib>

int main() {
  const sdl_painter::Pen pen(sdl_painter::Color{255, 0, 0, 255}, 2.0F);
  std::printf("sdl_painter %.*s, pen width %.1f\n",
              static_cast<int>(sdl_painter::kVersionString.size()),
              sdl_painter::kVersionString.data(), pen.GetWidth());

  // No window or GPU context. Application does not touch SDL until Run().
  const sdl_painter::Application app;
  auto renderer = sdl_painter::CreateRenderer(sdl_painter::RendererBackend::kOpenGL);
  return renderer != nullptr ? EXIT_SUCCESS : EXIT_FAILURE;
}
