from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rename, replace_in_file
import glob
import os

required_conan_version = ">=1.46.0"


class FoxiConan(ConanFile):
    name = "foxi"
    description = "ONNXIFI with Facebook Extension."
    license = "MIT"
    topics = ("foxi", "onnxifi")
    homepage = "https://github.com/houseroad/foxi"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
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
        tc.variables["FOXI_WERROR"] = False
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        replace_in_file(self, cmakelists, "add_msvc_runtime_flag(foxi_loader)", "")
        replace_in_file(self, cmakelists, "add_msvc_runtime_flag(foxi_dummy)", "")
        replace_in_file(self, cmakelists,
                              "DESTINATION lib",
                              "RUNTIME DESTINATION bin ARCHIVE DESTINATION lib LIBRARY DESTINATION lib")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        # Move plugin to bin folder on Windows
        for dll_file in glob.glob(os.path.join(self.package_folder, "lib", "*.dll")):
            rename(self, src=dll_file, dst=os.path.join(self.package_folder, "bin", os.path.basename(dll_file)))

    def package_info(self):
        self.cpp_info.libs = ["foxi_dummy", "foxi_loader"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["dl"]
