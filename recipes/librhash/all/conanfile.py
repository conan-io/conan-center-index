import os

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class LibRHashConan(ConanFile):
    name = "librhash"
    description = "Great utility for computing hash sums"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://rhash.sourceforge.net/"
    topics = ("rhash", "hash", "checksum")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, os.path.join(self.export_sources_folder, "src", "librhash"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _xversion(self):
        # https://github.com/rhash/RHash/blob/v1.4.4/configure#L339
        version = Version(self.version)
        return f"0x{version.major.value:02x}{version.minor.value:02x}{version.patch.value:02x}{0:02x}"

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["USE_OPENSSL"] = self.options.with_openssl
        tc.preprocessor_definitions["RHASH_XVERSION"] = self._xversion
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "librhash"))
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "LibRHash")
        self.cpp_info.set_property("cmake_target_name", "LibRHash::LibRHash")
        self.cpp_info.set_property("pkg_config_name", "librhash")
        self.cpp_info.libs = ["rhash"]
        self.cpp_info.defines.append(f"RHASH_XVERSION={self._xversion}")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "LibRHash"
        self.cpp_info.names["cmake_find_package_multi"] = "LibRHash"
