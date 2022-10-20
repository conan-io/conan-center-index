from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.46.0"


class JBigConan(ConanFile):
    name = "jbig"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ImageMagick/jbig"
    description = "jbig for the Windows build of ImageMagick"
    topics = ("jbig", "imagemagick", "window", "graphic")
    license = "GPL-2.0"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_executables": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_executables": True,
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

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
        tc.variables["JBIG_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["BUILD_EXECUTABLES"] = self.options.build_executables
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["jbig"]
        if self.options.shared and is_msvc(self):
            self.cpp_info.defines = ["_JBIGDLL_"]

        if self.options.build_executables:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
