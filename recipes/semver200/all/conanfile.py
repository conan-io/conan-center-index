from os.path import join
from conan import ConanFile
from conan.tools.files import apply_conandata_patches, copy, get
from conan.tools.build import check_min_cppstd
from conans import CMake
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.50.0"

class SemVer200Conan(ConanFile):
    name = "semver200"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/zmarko/semver"
    description = "Semantic versioning for cpp14"
    topics = ("versioning", "semver", "semantic")

    settings = "os", "compiler", "arch", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False, 
        "fPIC": True,
    }

    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(p["patch_file"])

    def validate(self):
        if self.info.settings.os == "Windows" and self.info.options.shared:
              raise ConanInvalidConfiguration("Shared library on Windows not supported")
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, 14)

    def configure(self):
        if self.options.shared or self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        apply_conandata_patches(self)
        cmake = self._configure_cmake()
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", join(self.source_folder, self._source_subfolder), join(self.package_folder, "licenses/"), keep_path=False)
        # Parent Build system does not support installation; so we must manually package
        hdr_src = join(self.source_folder, join(self._source_subfolder, "include"))
        hdr_dst = join(join(self.package_folder, "include"), self.name)
        copy(self, "*.h", hdr_src, hdr_dst, keep_path=True)
        copy(self, "*.inl", hdr_src, hdr_dst, keep_path=True)

        lib_dir = join(self.package_folder, "lib")
        copy(self, "*.a", self.build_folder, lib_dir, keep_path=False)
        copy(self, "*.lib", self.build_folder, lib_dir, keep_path=False)
        copy(self, "*.so", self.build_folder, lib_dir, keep_path=False)
        copy(self, "*.dylib", self.build_folder, lib_dir, keep_path=False)
        copy(self, "*.dll*", self.build_folder, join(self.package_folder, "bin"), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["semver"]
