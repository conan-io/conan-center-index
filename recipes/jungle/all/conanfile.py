from os.path import join
from conan import ConanFile
from conan.tools.files import apply_conandata_patches, copy, get
from conan.tools.build import check_min_cppstd
from conans import CMake

required_conan_version = ">=1.50.0"

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
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        src_dir = join(self.source_folder, self._source_subfolder)
        copy(self, "LICENSE*", src_dir, join(self.package_folder, "licenses"))

        hdr_src = join(src_dir, "include")
        copy(self, "*.h", hdr_src, join(self.package_folder, "include"), keep_path=True)

        lib_dir = join(self.package_folder, "lib")
        copy(self, "*.a", self.build_folder, lib_dir, keep_path=False)
        copy(self, "*.lib", self.build_folder, lib_dir, keep_path=False)
        copy(self, "*.so*", self.build_folder, lib_dir, keep_path=False)
        copy(self, "*.dylib*", self.build_folder, lib_dir, keep_path=False)
        copy(self, "*.dll*", self.build_folder, join(self.package_folder, "bin"), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["jungle"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "dl"])
