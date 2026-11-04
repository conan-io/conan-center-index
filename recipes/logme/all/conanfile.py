from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout, CMakeToolchain, CMakeDeps
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy, rmdir
import os

required_conan_version = ">=2.1"

class LogmeConan(ConanFile):
    name = "logme"
    package_type = "library"

    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/efmsoft/logme"
    description = "Lightweight cross-platform C/C++ logging framework."
    topics = ("logging", "log", "logger", "console", "file")

    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]

    def validate(self):
        check_min_cppstd(self, 20)

    def requirements(self):
        # INFO: Transitive headers: Logme/Utils.h:#include <json/json.h>
        self.requires("jsoncpp/[>=1.9.6 <2]", transitive_headers=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][str(self.version)], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)

        tc.cache_variables["LOGME_BUILD_EXAMPLES"] = False
        tc.cache_variables["LOGME_BUILD_TESTS"] = False
        tc.cache_variables["LOGME_BUILD_TOOLS"] = False
        tc.cache_variables["LOGME_ENABLE_INSTALL"] = True

        tc.cache_variables["LOGME_BUILD_STATIC"] = not self.options.shared
        tc.cache_variables["LOGME_BUILD_DYNAMIC"] = self.options.shared
        tc.cache_variables["USE_JSONCPP"] = True

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["logmed" if self.options.shared else "logme"]
        self.cpp_info.defines.append("USE_JSONCPP")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
