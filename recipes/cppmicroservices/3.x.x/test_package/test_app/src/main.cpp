#include <chrono>
#include <iostream>
#include <filesystem>
#include <functional>
#include <deque>

#include <cppmicroservices/GlobalConfig.h>
#include <cppmicroservices/Bundle.h>
#include <cppmicroservices/BundleContext.h>
#include <cppmicroservices/BundleImport.h>
#include <cppmicroservices/Framework.h>
#include <cppmicroservices/FrameworkEvent.h>
#include <cppmicroservices/FrameworkFactory.h>

#if defined(_WIN32) || defined(_WIN64)
    #define LIB_EXT ".dll"
    #define LIB_PREFIX
#elif defined(__APPLE__) || defined(__MACH__)
    #define LIB_EXT ".dylib"
    #define LIB_PREFIX "lib"
#elif defined(__linux__)
    #define LIB_EXT ".so"
    #define LIB_PREFIX "lib"
#endif

namespace {
    // from: https://stackoverflow.com/questions/10270328/the-simplest-and-neatest-c11-scopeguard/28413370#28413370
    class scope_guard {
    public:
        enum execution { always, no_exception, exception };
        
        scope_guard(scope_guard &&) = default;
        explicit scope_guard(execution policy = always) : policy(policy) {}
        
        template<class Callable>
        scope_guard(Callable && func, execution policy = always) : policy(policy) {
            this->operator += <Callable>(std::forward<Callable>(func));
        }
        
        template<class Callable>
        scope_guard& operator += (Callable && func) try {
            handlers.emplace_front(std::forward<Callable>(func));
            return *this;
        } catch(...) {
            if(policy != no_exception) func();
            throw;
        }
        
        ~scope_guard() {
            if(policy == always || (std::uncaught_exception() == (policy == exception))) {
                for(auto &f : handlers) try {
                        f(); // must not throw
                    } catch(...) { /* std::terminate(); ? */ }
            }
        }
        
        void dismiss() noexcept {
            handlers.clear();
        }
        
    private:
        scope_guard(const scope_guard&) = delete;
        void operator = (const scope_guard&) = delete;
        
        std::deque<std::function<void()>> handlers;
        execution policy = always;
    };
}

class US_ABI_IMPORT TestBundle
{
public:
    virtual ~TestBundle() = default;
    virtual std::string Description() const = 0;
};

#define STRINGIFY(x) #x
#define TOSTRING(x) STRINGIFY(x)

int main(int, char**) {
  // Set up cppms framework
  auto framework = cppmicroservices::FrameworkFactory().NewFramework();
  try {
    framework.Start();

    // make sure to stop the framework on exit
    scope_guard on_exit = [&]() {
        framework.Stop();
        framework.WaitForStop(std::chrono::milliseconds::zero());
    };
    auto context = framework.GetBundleContext();
    
    // Initialize DeclarativeServices
    std::string ds_dll_path = TOSTRING(DS_DLL_PATH);
    auto ds_bundles = context.InstallBundles(ds_dll_path);
    std::for_each(ds_bundles.begin(), ds_bundles.end(), [](auto& bundle) { bundle.Start(); });

    // Now install/start test_bundle
    auto bundle_path_str = std::string(BINARY_PATH) + "/" + LIB_PREFIX + "test_bundle" + LIB_EXT;
    auto bundles = context.InstallBundles(bundle_path_str);
    std::for_each(bundles.begin(), bundles.end(), [](auto& bundle) { bundle.Start(); });

    // Finally, get the service in test_bundle and call the Description() method.
    auto sRef = context.GetServiceReference<TestBundle>();
    auto service = context.GetService<TestBundle>(sRef);
    std::cout << service->Description() << std::endl;
    
  } catch (std::exception const& e) {
    std::cerr << e.what() << std::endl;
    return 1;
  }

  return 0;
}
