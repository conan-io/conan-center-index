from conan import ConanFile
from conan.tools.files import get, copy, get, rm, rmdir
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps

import os

class MsgpackConan(ConanFile):
    name = "msgpack"
    description = "The official C++ library for MessagePack"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/msgpack/msgpack-c"
    topics = ("conan", "msgpack", "message-pack", "serialization")
    license = "BSL-1.0"

    settings = "os", "arch", "build_type", "compiler"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        "c_api": [True, False],
        "cpp_api": [True, False],
        "with_boost": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
        "c_api": True,
        "cpp_api": True,
        "with_boost": False,
    }
    deprecated = "msgpack-c or msgpack-cxx"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if not self.options.c_api and not self.options.cpp_api:
            raise ConanInvalidConfiguration("You must enable at least c_api or cpp_api.")
        if self.options.c_api:
            if self.options.shared:
                del self.options.fPIC
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd
        else:
            self.header_only = True
            del self.options.shared
            del self.options.fPIC
        if not self.options.cpp_api:
            del self.options.with_boost
        if self.options.get_safe("with_boost"):
            self.options["boost"].header_only = False
            self.options["boost"].without_chrono = False
            self.options["boost"].without_context = False
            self.options["boost"].without_system = False
            self.options["boost"].without_timer = False

    def requirements(self):
        if self.options.get_safe("with_boost"):
            self.requires("boost/1.74.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        if self.options.c_api:
            toolchain = CMakeToolchain(self)
            toolchain.variables["MSGPACK_ENABLE_SHARED"] = self.options.shared
            toolchain.variables["MSGPACK_ENABLE_STATIC"] = not self.options.shared
            toolchain.variables["MSGPACK_ENABLE_CXX"] = self.options.cpp_api
            toolchain.variables["MSGPACK_BOOST"] = self.options.get_safe("with_boost", False)
            toolchain.variables["MSGPACK_32BIT"] = self.settings.arch == "x86"
            toolchain.variables["MSGPACK_BUILD_EXAMPLES"] = False
            toolchain.variables["MSGPACK_BUILD_TESTS"] = False
            toolchain.generate()

            deps = CMakeDeps(self)
            deps.generate()

    def build(self):
        if self.options.c_api:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def package_id(self):
        self.info.clear()

    def package(self):
        copy(self, "LICENSE_1_0.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        if self.options.c_api:
            cmake = CMake(self)
            cmake.configure()
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        else:
            copy(self, "*.h", os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
            copy(self, "*.hpp", os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        # TODO: CMake imported targets shouldn't be namespaced (waiting implementation of https://github.com/conan-io/conan/issues/7615)
        if self.options.c_api:
            self.cpp_info.components["msgpackc"].names["cmake_find_package"] = "msgpackc"
            self.cpp_info.components["msgpackc"].names["cmake_find_package_multi"] = "msgpackc"
            self.cpp_info.components["msgpackc"].libs = ["msgpackc"]
        if self.options.cpp_api:
            self.cpp_info.components["msgpackc-cxx"].names["cmake_find_package"] = "msgpackc-cxx"
            self.cpp_info.components["msgpackc-cxx"].names["cmake_find_package_multi"] = "msgpackc-cxx"
            if self.options.with_boost:
                self.cpp_info.components["msgpackc-cxx"].defines = ["MSGPACK_USE_BOOST"]
                self.cpp_info.components["msgpackc-cxx"].requires = ["boost::boost"]
