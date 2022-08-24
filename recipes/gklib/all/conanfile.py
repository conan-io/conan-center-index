from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches

required_conan_version = ">=1.43.0"


class GKlibConan(ConanFile):
    name = "gklib"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/KarypisLab/GKlib"
    description = "A library of various helper routines and frameworks" \
                  " used by many of the lab's software"
    topics = ("karypislab")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
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

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.options.shared and self._is_msvc:
            raise ConanInvalidConfiguration(
                f"{self.name} {self.version} shared not supported with Visual Studio")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        apply_conandata_patches(self)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["ASSERT"] = self.settings.build_type == "Debug"
            self._cmake.definitions["ASSERT2"] = self.settings.build_type == "Debug"
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.libs = ["GKlib"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
        if self._is_msvc or self._is_mingw:
            self.cpp_info.defines.append("USE_GKREGEX")
        if self._is_msvc:
            self.cpp_info.defines.append("__thread=__declspec(thread)")
