from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, patch
from conans import CMake
from conans.tools import check_min_cppstd

class NuRaftConan(ConanFile):
    name = "nuraft"
    homepage = "https://github.corp.ebay.com/sds/NuRaft"
    description = """Cornerstone based RAFT library."""
    topics = ("raft")
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"

    settings = "os", "compiler", "arch", "build_type"

    options = {
        "shared": ['True', 'False'],
        "fPIC": ['True', 'False'],
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
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def requirements(self):
        self.requires("boost/1.79.0")
        self.requires("openssl/1.1.1q")

    def validate(self):
        if self.settings.os in ["Macos"] and self.options.shared:
            raise ConanInvalidConfiguration("Building Shared Object for {} unsupported".format(self.settings.os))
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def cmakeGet(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        for patch_file in self.conan_data.get("patches", {}).get(self.version, []):
            patch(self, **patch_file)
        cmake = self.cmakeGet()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses/", src=self._source_subfolder )
        self.copy("*.a", dst="lib", src="lib", symlinks=False)
        self.copy("*.lib", dst="lib", src="lib", symlinks=False)
        self.copy("*.so*", dst="lib", src="lib", symlinks=True)
        self.copy("*.dylib*", dst="lib", src="lib", symlinks=True)
        self.copy("*.dll*", dst="lib", src="lib")
        self.copy("*.hxx", dst="include/", src="%s/include" % (self._source_subfolder), keep_path=True)
        self.copy("*in_memory_log_store.hxx", dst="include/libnuraft", keep_path=False)
        self.copy("*callback.h", dst="include/libnuraft", keep_path=False)
        self.copy("*event_awaiter.h", dst="include/libnuraft", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["nuraft"]
        if self.settings.os != "Windows":
            self.cpp_info.system_libs.extend(["pthread"])
