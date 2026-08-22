from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.53.0"


class JxrlibConan(ConanFile):
    name = "jxrlib"
    description = "jxrlib is JPEG XR Image Codec reference implementation library released by Microsoft under BSD-2-Clause License."
    homepage = "https://jxrlib.codeplex.com/"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-2-Clause"
    topics = ("jxr", "jpeg", "xr")
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

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if is_msvc(self) and self.info.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} shared not supported by Visual Studio")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["JPEGXR_FOLDER"] = self.source_folder.replace("\\", "/")
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libjxr")
        self.cpp_info.libs = ["jxrglue", "jpegxr"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
        if not is_msvc(self):
            self.cpp_info.defines.append("__ANSI__")

        # TODO: to remove in conan v2, and do not port this to CMakeDeps, it was a mistake
        self.cpp_info.names["cmake_find_package"] = "JXR"
        self.cpp_info.names["cmake_find_package_multi"] = "JXR"
