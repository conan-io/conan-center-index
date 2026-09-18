#include "IGreeter.h"

#include <cppmicroservices/Bundle.h>
#include <cppmicroservices/BundleContext.h>
#include <cppmicroservices/Framework.h>
#include <cppmicroservices/FrameworkEvent.h>
#include <cppmicroservices/FrameworkFactory.h>

#ifdef HAS_COMPENDIUM
#    include <cppmicroservices/servicecomponent/runtime/ServiceComponentRuntime.hpp>
#endif

#include <cstdlib>
#include <filesystem>
#include <iostream>
#include <string>
#include <vector>

#ifdef HAS_COMPENDIUM
namespace scr = cppmicroservices::service::component::runtime;
#endif

namespace
{

std::string
FindLibrary(std::string const& dir, std::string const& baseName)
{
    namespace fs = std::filesystem;
#if defined(_WIN32)
    std::string const ext = ".dll";
    std::string const prefix = "";
#elif defined(__APPLE__)
    std::string const ext = ".dylib";
    std::string const prefix = "lib";
#else
    std::string const ext = ".so";
    std::string const prefix = "lib";
#endif

    // Exact match first
    auto exact = fs::path(dir) / (prefix + baseName + ext);
    if (fs::exists(exact))
    {
        return exact.string();
    }

    // Search for versioned variants (e.g., DeclarativeServices1.dll)
    for (auto const& entry : fs::directory_iterator(dir))
    {
        auto filename = entry.path().filename().string();
        if (filename.find(baseName) == 0 && entry.path().extension() == ext)
        {
            return entry.path().string();
        }
    }

    return exact.string();
}

} // namespace

int
main(int, char*[])
{
    std::string const bundleDir = TEST_BUNDLE_DIR;
#ifdef HAS_COMPENDIUM
    std::string const packageLibDir = US_PACKAGE_BUNDLE_DIR;
#endif

    auto framework = cppmicroservices::FrameworkFactory().NewFramework();
    framework.Init();

    auto ctx = framework.GetBundleContext();
    if (!ctx)
    {
        std::cerr << "Invalid framework context" << std::endl;
        return EXIT_FAILURE;
    }

    framework.Start();

#ifdef HAS_COMPENDIUM
    // Install and start DeclarativeServices from the package
    auto dsBundles = ctx.InstallBundles(FindLibrary(packageLibDir, "DeclarativeServices"));
    if (dsBundles.empty())
    {
        std::cerr << "Failed to install DeclarativeServices bundle" << std::endl;
        return EXIT_FAILURE;
    }
    for (auto& b : dsBundles)
    {
        b.Start();
    }

    // Verify ServiceComponentRuntime is available
    auto scrRef = ctx.GetServiceReference<scr::ServiceComponentRuntime>();
    if (!scrRef)
    {
        std::cerr << "ServiceComponentRuntime service not available" << std::endl;
        return EXIT_FAILURE;
    }
    auto scrService = ctx.GetService<scr::ServiceComponentRuntime>(scrRef);
    if (!scrService)
    {
        std::cerr << "Failed to get ServiceComponentRuntime service" << std::endl;
        return EXIT_FAILURE;
    }

    // Install and start the DS test bundle
    auto testBundles = ctx.InstallBundles(FindLibrary(bundleDir, "test_greeter_ds"));
    if (testBundles.empty())
    {
        std::cerr << "Failed to install test_greeter_ds bundle" << std::endl;
        return EXIT_FAILURE;
    }
    for (auto& b : testBundles)
    {
        b.Start();
    }

    // Verify component is registered via SCR introspection
    auto descriptions = scrService->GetComponentDescriptionDTOs();
    bool found = false;
    for (auto const& desc : descriptions)
    {
        if (desc.implementationClass == "GreeterDSImpl")
        {
            found = true;
            break;
        }
    }
    if (!found)
    {
        std::cerr << "GreeterDSImpl component not found in SCR" << std::endl;
        return EXIT_FAILURE;
    }

#else
    // Install and start the activator test bundle
    auto testBundles = ctx.InstallBundles(FindLibrary(bundleDir, "test_greeter_activator"));
    if (testBundles.empty())
    {
        std::cerr << "Failed to install test_greeter_activator bundle" << std::endl;
        return EXIT_FAILURE;
    }
    for (auto& b : testBundles)
    {
        b.Start();
    }
#endif

    // Query for the IGreeter service
    auto greeterRef = ctx.GetServiceReference<IGreeter>();
    if (!greeterRef)
    {
        std::cerr << "IGreeter service not available" << std::endl;
        return EXIT_FAILURE;
    }
    auto greeter = ctx.GetService<IGreeter>(greeterRef);
    if (!greeter)
    {
        std::cerr << "Failed to get IGreeter service" << std::endl;
        return EXIT_FAILURE;
    }

    std::string greeting = greeter->Greet();
    std::cout << "Service returned: " << greeting << std::endl;

#ifdef HAS_COMPENDIUM
    if (greeting != "Hello from DS!")
    {
        std::cerr << "Unexpected greeting from DS bundle" << std::endl;
        return EXIT_FAILURE;
    }
#else
    if (greeting != "Hello from Activator!")
    {
        std::cerr << "Unexpected greeting from activator bundle" << std::endl;
        return EXIT_FAILURE;
    }
#endif

    framework.Stop();
    framework.WaitForStop(std::chrono::milliseconds::zero());

    std::cout << "Test passed!" << std::endl;
    return EXIT_SUCCESS;
}
