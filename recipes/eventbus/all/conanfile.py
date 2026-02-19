from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rmdir
from conan.tools.build import check_min_cppstd
import os


class EventBusConan(ConanFile):
    name = "eventbus"
    description = "Simple and fast event bus"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/gelldur/EventBus"
    topics = ("observer-pattern", "event-dispatcher", "signal", "slot", "publish-subscribe", "thread-safe")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 17

    # The actual sources are in `lib` subdirectory
    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "lib")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)


    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["ENABLE_TEST"] = False
        tc.cache_variables["ENABLE_PERFORMANCE"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=self._source_subfolder)
        cmake.build()


    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "EventBus")
        self.cpp_info.set_property("cmake_target_name", "Dexode::EventBus")

        self.cpp_info.libs = ["EventBus"]
        
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]

        self.cpp_info.names["cmake_find_package"] = "Dexode"
        self.cpp_info.components["EventBus"].names["cmake_find_package"] = "EventBus"
        self.cpp_info.components["EventBus"].libs = ["EventBus"]
