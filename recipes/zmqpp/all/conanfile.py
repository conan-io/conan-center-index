from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
import os

required_conan_version = ">=1.53.0"


class ZmqppConan(ConanFile):
    name = "zmqpp"
    description = (
        "This C++ binding for 0mq/zmq is a 'high-level' library that hides "
        "most of the c-style interface core 0mq provides."
    )
    license = "MPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/zeromq/zmqpp"
    topics = ("zmq", "0mq", "zeromq", "message-queue", "asynchronous")
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
        return 11

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zeromq/4.3.4", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # No bool cast until https://github.com/conan-io/conan/pull/12086 (conan 1.53.0)
        tc.cache_variables["ZMQPP_LIBZMQ_CMAKE"] = "ON"
        tc.cache_variables["ZMQPP_BUILD_STATIC"] = "OFF" if self.options.shared else "ON"
        tc.cache_variables["ZMQPP_BUILD_SHARED"] = "ON" if self.options.shared else "OFF"
        tc.cache_variables["ZMQPP_BUILD_EXAMPLES"] = "OFF"
        tc.cache_variables["ZMQPP_BUILD_CLIENT"] = "OFF"
        tc.cache_variables["ZMQPP_BUILD_TESTS"] = "OFF"
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libzmqpp")
        self.cpp_info.libs = ["zmqpp" if self.options.shared else "zmqpp-static"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
