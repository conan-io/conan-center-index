from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout

import os

required_conan_version = ">=1.47.0"

class QuickJSConan(ConanFile):
    name = "quickjs"
    description = "QuickJS is a small and embeddable Javascript engine."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://bellard.org/quickjs/"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_bignum": [True, False],
        "dump_leaks": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_bignum" : True,
        "dump_leaks": False,
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["QUICKJS_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["USE_BIGNUM"] = self.options.use_bignum
        tc.variables["DUMP_LEAKS"] = self.options.dump_leaks
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["quickjs"]

        if self.options.use_bignum == True:
            self.cpp_info.defines.append("CONFIG_BIGNUM")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("dl")
            self.cpp_info.system_libs.append("m")
