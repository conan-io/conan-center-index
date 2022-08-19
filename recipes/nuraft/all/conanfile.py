from os.path import join
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, apply_conandata_patches
from conans import CMake
from conans.tools import check_min_cppstd

required_conan_version = ">=1.50.0"

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
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(p["patch_file"])

    def requirements(self):
        self.requires("boost/1.79.0")
        self.requires("openssl/1.1.1q")

    def validate(self):
        if self.info.settings.os in ["Macos"] and self.options.shared:
            raise ConanInvalidConfiguration("Building Shared Object for {} unsupported".format(self.settings.os))
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def configure(self):
        if self.options.shared or self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def cmakeGet(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        apply_conandata_patches(self)
        cmake = self.cmakeGet()
        cmake.build()

    def package(self):
        lib_dir = join(self.package_folder, "lib")
        copy(self, "LICENSE", join(self.source_folder, self._source_subfolder), join(self.package_folder, "licenses/"), keep_path=False)
        copy(self, "*.lib", self.build_folder, lib_dir, keep_path=False)
        copy(self, "*.a", self.build_folder, lib_dir, keep_path=False)
        copy(self, "*.so*", self.build_folder, lib_dir, keep_path=False)
        copy(self, "*.dylib*", self.build_folder, lib_dir, keep_path=False)
        copy(self, "*.dll*", self.build_folder, join(self.package_folder, "bin"), keep_path=False)

        hdr_src = join(self.source_folder, join(self._source_subfolder, "include"))
        hdr_dir = join(self.package_folder, join("include", "libnuraft"))

        copy(self, "*.hxx", hdr_src, join(self.package_folder, "include"), keep_path=True)
        copy(self, "*in_memory_log_store.hxx", self.source_folder, hdr_dir, keep_path=False)
        copy(self, "*callback.h", self.source_folder, hdr_dir, keep_path=False)
        copy(self, "*event_awaiter.h", self.source_folder, hdr_dir, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["nuraft"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread"])
