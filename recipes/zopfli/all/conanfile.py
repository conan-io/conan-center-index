from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=1.50.0"


class ZopfliConan(ConanFile):
    name = "zopfli"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/zopfli/"
    description = (
        "Zopfli Compression Algorithm is a compression library programmed in C "
        "to perform very good, but slow, deflate or zlib compression."
    )
    topics = ("zopfli", "compression", "deflate", "gzip", "zlib")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
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
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ZOPFLI_BUILD_INSTALL"] = True
        tc.variables["CMAKE_MACOSX_BUNDLE"] = False
        # Generate a relocatable shared lib on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Zopfli")

        self.cpp_info.components["libzopfli"].set_property("cmake_target_name", "Zopfli::libzopfli")
        self.cpp_info.components["libzopfli"].libs = ["zopfli"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libzopfli"].system_libs = ["m"]

        self.cpp_info.components["libzopflipng"].set_property("cmake_target_name", "Zopfli::libzopflipng")
        self.cpp_info.components["libzopflipng"].libs = ["zopflipng"]
        self.cpp_info.components["libzopflipng"].requires = ["libzopfli"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "Zopfli"
        self.cpp_info.names["cmake_find_package_multi"] = "Zopfli"
        self.cpp_info.components["libzopfli"].names["cmake_find_package"] = "libzopfli"
        self.cpp_info.components["libzopfli"].names["cmake_find_package_multi"] = "libzopfli"
        self.cpp_info.components["libzopflipng"].names["cmake_find_package"] = "libzopflipng"
        self.cpp_info.components["libzopflipng"].names["cmake_find_package_multi"] = "libzopflipng"
