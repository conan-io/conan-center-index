from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain, CMakeDeps
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=2.1"

class ToomanycooksConan(ConanFile):
    name = "toomanycooks"
    description = "The C++20 coroutine framework with no compromises. Excellent performance, simple syntax, and powerful features."
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tzcnt/TooManyCooks"
    topics = ("tasking", "coroutine", "thread-pool", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    implements = ["auto_header_only"]
    options = {
        "with_hwloc": [True, False],
        "with_asio": [None, "standalone", "boost"],
    }
    default_options = {
        "with_hwloc": True,
        "with_asio": None,
    }

    def requirements(self):
        if self.options.with_hwloc:
            self.requires("hwloc/[>=2.4]")
        if self.options.with_asio == "standalone":
            self.requires("asio/[>=1.28 <2]")
        if self.options.with_asio == "boost":
            self.requires("boost/[>=1.84 <1.92]")

    def validate(self):
        if self.settings.compiler == "msvc":
            raise ConanInvalidConfiguration(
                "TooManyCooks is currently unsupported with MSVC due to a compiler bug: "
                "https://developercommunity.visualstudio.com/t/MSVC-incorrectly-caches-thread_local-var/11041371"
            )
        check_min_cppstd(self, 20)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeDeps(self)
        tc.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["TMC_USE_HWLOC"] = self.options.with_hwloc
        tc.variables["TMC_USE_BOOST_ASIO"] = self.options.with_asio == "boost"
        tc.generate()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.configure()
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "TooManyCooks")
        self.cpp_info.set_property("cmake_target_name", "TooManyCooks::TooManyCooks")

        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        if self.options.with_hwloc:
            self.cpp_info.defines.append("TMC_USE_HWLOC")
        if self.options.with_asio == "boost":
            self.cpp_info.defines.append("TMC_USE_BOOST_ASIO")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
