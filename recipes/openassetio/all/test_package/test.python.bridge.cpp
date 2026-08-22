#include <memory>

#include <Python.h>

#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/hostApi/ManagerImplementationFactoryInterface.hpp>
#include <openassetio/python/hostApi.hpp>

namespace {
struct DummyLoggerInterface : openassetio::log::LoggerInterface {
  void log(Severity severity, const openassetio::Str& message) override {}
};
}  // namespace

int main() {
  Py_Initialize();
  auto logger = std::make_shared<DummyLoggerInterface>();
  {
    const auto factory =
        openassetio::python::hostApi::createPythonPluginSystemManagerImplementationFactory(logger);
    const auto identifiers = factory->identifiers();
    // Must be destroyed before Py_FinalizeEx.
  }
  Py_FinalizeEx();
}
