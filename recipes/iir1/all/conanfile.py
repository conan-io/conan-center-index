from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class Iir1Conan(ConanFile):
    name = "iir1"
    license = "MIT"
    description = (
        "An infinite impulse response (IIR) filter library for Linux, Mac OSX "
        "and Windows which implements Butterworth, RBJ, Chebychev filters and "
        "can easily import coefficients generated by Python (scipy)."
    )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/berndporr/iir1"
    topics = ("dsp", "signals", "filtering")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "noexceptions": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "noexceptions": False,
    }

    @property
    def _min_cppstd(self):
        return "11"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "1.9.1":
            del self.options.noexceptions

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.options.get_safe("noexceptions"):
            tc.preprocessor_definitions["IIR1_NO_EXCEPTIONS"] = "1"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        if self.options.shared:
            rm(self, "*iir_static.*", os.path.join(self.package_folder, "lib"))
        else:
            rmdir(self, os.path.join(self.package_folder, "bin"))
            rm(self, "*iir.*", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        name = "iir" if self.options.shared else "iir_static"
        self.cpp_info.set_property("cmake_file_name", "iir")
        self.cpp_info.set_property("cmake_target_name", f"iir::{name}")
        self.cpp_info.set_property("pkg_config_name", "iir")
        # TODO: back to global scope in conan v2
        self.cpp_info.components["iir"].libs = [name]
        if self.options.get_safe("noexceptions"):
            self.cpp_info.components["iir"].defines.append("IIR1_NO_EXCEPTIONS")

        # TODO: to remove in conan v2
        self.cpp_info.names["cmake_find_package"] = "iir"
        self.cpp_info.names["cmake_find_package_multi"] = "iir"
        self.cpp_info.components["iir"].names["cmake_find_package"] = name
        self.cpp_info.components["iir"].names["cmake_find_package_multi"] = name
        self.cpp_info.components["iir"].set_property("cmake_target_name", f"iir::{name}")
