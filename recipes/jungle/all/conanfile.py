from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, patch
from conans import CMake
from conans.tools import check_min_cppstd

required_conan_version = ">=1.33.0"

class JungleConan(ConanFile):
    name = "jungle"
    homepage = "https://github.com/eBay/Jungle"
    description = "Key-value storage library, based on a combined index of LSM-tree and copy-on-write B+tree"
    topics = ("kv-store", "cow")
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"

    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch_file in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch_file["patch_file"])

    def requirements(self):
        self.requires("forestdb/cci.20220727")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def build(self):
        for patch_file in self.conan_data.get("patches", {}).get(self.version, []):
            patch(self, **patch_file)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE*", src=self._source_subfolder, dst="licenses")
        self.copy("*.a*", dst="lib", src="lib")
        self.copy("*.lib", dst="lib", src="lib")
        self.copy("*.so*", dst="lib", src="lib", symlinks=True)
        self.copy("*.dylib*", dst="lib", src="lib", symlinks=True)
        self.copy("*.dll*", dst="lib", src="lib")
        self.copy("*.h", dst="include/", src="%s/include" % (self._source_subfolder), keep_path=True)

    def package_info(self):
        self.cpp_info.libs = ["jungle"]
        self.cpp_info.system_libs.extend(["pthread", "dl"])
