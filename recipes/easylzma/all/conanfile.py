import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, load, save
from conan.tools.microsoft import is_msvc, msvc_runtime_flag

required_conan_version = ">=1.53.0"


class EazylzmaConan(ConanFile):
    name = "easylzma"
    description = (
        "An easy to use, tiny, public domain, C wrapper library around "
        "Igor Pavlov's work that can be used to compress and extract lzma files"
    )
    license = "DocumentRef-README:LicenseRef-PublicDomain-WITH-Attribution" # Public Domain with attribution request
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lloyd/easylzma"
    topics = ("lzma",)

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
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # Relocatable shared libs on macOS
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        # Silence CMake warning about LOCATION property
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0026"] = "OLD"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target=self._libname)

    @property
    def _license_text(self):
        # Extract the License/s from the README to a file
        tmp = load(self, os.path.join(self.source_folder, "README"))
        return tmp[tmp.find("License", 1) : tmp.find("work.", 1) + 5]

    def package(self):
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._license_text)
        for pattern in ["*.lib", "*.a", "*.so*", "*.dylib"]:
            copy(self, pattern,
                 dst=os.path.join(self.package_folder, "lib"),
                 src=self.build_folder,
                 keep_path=False)
        copy(self, "*.dll",
             dst=os.path.join(self.package_folder, "bin"),
             src=self.build_folder,
             keep_path=False)
        copy(self, "easylzma/*",
             dst=os.path.join(self.package_folder, "include"),
             src=os.path.join(self.source_folder, "src"))

    @property
    def _libname(self):
        return "easylzma" if self.options.shared else "easylzma_s"

    def package_info(self):
        self.cpp_info.libs = [self._libname]
        if self.options.shared:
            self.cpp_info.defines = ["EASYLZMA_SHARED"]
        if is_msvc(self):
            if "d" in msvc_runtime_flag(self):
                self.cpp_info.defines.append("DEBUG")
