#include <RmlUi/Core.h>

class DummyRenderInterface : public Rml::RenderInterface {
public:
  virtual void EnableScissorRegion(bool) override {}
  virtual void RenderGeometry(Rml::Vertex *, int, int *, int,
                              Rml::TextureHandle,
                              const Rml::Vector2f &) override {}
  virtual void SetScissorRegion(int, int, int, int) override {}
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
