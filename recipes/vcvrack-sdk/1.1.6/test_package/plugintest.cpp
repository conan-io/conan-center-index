#include <rack.hpp>

//check for availability of deps/include from SDK
#include <speex/speex_resampler.h>
#include <nanovg_gl.h>


namespace vcvracksdktest {

class TestModule : public rack::Module
{
 public:

  enum ParamIds {
    NUM_PARAMS
  };

  enum InputIds {
    NUM_INPUTS
  };

  enum OutputIds {
    NUM_OUTPUTS
  };

  enum LightIds {
    NUM_LIGHTS
  };

  TestModule() : Module()
  {
    config(NUM_PARAMS, NUM_INPUTS, NUM_OUTPUTS, NUM_LIGHTS);
  }

  virtual ~TestModule() = default;

  void process(const ProcessArgs& args) override { }
};

class TestWidget : public rack::ModuleWidget
{
 public:

  TestWidget(TestModule* module) : ModuleWidget(), _module(module)
  {
    setModule(module);
  }

  virtual ~TestWidget() = default;

  void step() override
  {
    ModuleWidget::step();
  }

  void draw(const DrawArgs& args) override
  {
    ModuleWidget::draw(args);
  }

 private:

  TestModule* _module;
};

}

rack::plugin::Plugin* pluginInstance;

rack::Model* modelTestPlugin = rack::createModel<vcvracksdktest::TestModule, vcvracksdktest::TestWidget>("TestModule");

void init(rack::plugin::Plugin* p) {
   pluginInstance = p;
   p->addModel(modelTestPlugin);
}
