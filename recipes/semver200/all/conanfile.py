import os
from conan import ConanFile
from conan.tools.files import get, patch
from conans.tools import check_min_cppstd
from conans import CMake

required_conan_version = ">=1.47.0"

class SemVer200Conan(ConanFile):
    name = "semver200"
    version = "1.1.0"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/zmarko/semver"
    description = "Semantic versioning for cpp14"
    topics = ("versioning", "semver", "semantic", "versioning")

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
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 14)

    def configure(self):
        if self.options.shared:
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
        for patch_file in self.conan_data.get("patches", {}).get(self.version, []):
            patch(self, **patch_file)
        cmake = self._configure_cmake()
        cmake.configure()
        cmake.build()

    def package(self):
        # Parent Build system does not support installation; so we must manually package
        self.copy("*.a*", dst="lib", src="lib")
        self.copy("*.lib", dst="lib", src="lib")
        self.copy("*.so*", dst="lib", src="lib", symlinks=True)
        self.copy("*.dylib*", dst="lib", src="lib", symlinks=True)
        self.copy("*.dll*", dst="lib", src="lib")
        self.copy("*.h", dst=os.path.join("include", self.name), src=os.path.join(self._source_subfolder, "include"), keep_path=True)
        self.copy("*.inl", dst=os.path.join("include", self.name), src=os.path.join(self._source_subfolder, "include"), keep_path=True)
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.libs = ["semver"]
