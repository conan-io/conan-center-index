#include <RmlUi/Core.h>

class DummyRenderInterface : public Rml::RenderInterface {
public:
  Rml::CompiledGeometryHandle CompileGeometry(Rml::Span<const Rml::Vertex>, Rml::Span<const int>) override { return {}; }
  void RenderGeometry(Rml::CompiledGeometryHandle, Rml::Vector2f, Rml::TextureHandle) override {}
  void ReleaseGeometry(Rml::CompiledGeometryHandle) override {}

  Rml::TextureHandle LoadTexture(Rml::Vector2i&, const Rml::String&) override { return {}; }
  Rml::TextureHandle GenerateTexture(Rml::Span<const unsigned char>, Rml::Vector2i) override { return {}; }
  void ReleaseTexture(Rml::TextureHandle) override {}

  void EnableScissorRegion(bool) override {}
  void SetScissorRegion(Rml::Rectanglei) override {}
};

class DummySystemInterface : public Rml::SystemInterface {
public:
  virtual double GetElapsedTime() override { return 0; }
};

int main() {
  DummyRenderInterface dummyRenderInterface;
  DummySystemInterface dummySystemInterface;

  Rml::SetRenderInterface(&dummyRenderInterface);
  Rml::SetSystemInterface(&dummySystemInterface);

  Rml::Initialise();
  Rml::Shutdown();

  return 0;
}
