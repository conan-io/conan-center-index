from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class LibaecConan(ConanFile):
    name = "libaec"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.dkrz.de/k202009/libaec"
    description = "Adaptive Entropy Coding library"
    topics = ("dsp", "libaec", "encoding", "decoding",)
    settings = "os", "compiler", "build_type", "arch"
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
        if tools.Version(self.version) >= "1.0.6" and self._is_msvc:
            # libaec/1.0.6 uses "restrict" keyword which seems to be supported since Visual Studio 16.
            if tools.Version(self.settings.compiler.version) < "16":
                raise ConanInvalidConfiguration("{} does not support Visual Studio {}".format(self.name, self.settings.compiler.version))
            # In libaec/1.0.6, fail to build aec_client command with debug and shared settings in Visual Studio.
            # Temporary, this recipe doesn't support these settings.
            if self.options.shared and self.settings.build_type == "Debug":
                raise ConanInvalidConfiguration("{} does not support debug and shared build in Visual Studio(currently)".format(self.name))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if tools.Version(self.version) < "1.0.6":
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                                  "add_subdirectory(tests)", "")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        if tools.Version(self.version) < "1.0.6":
            self.copy(pattern="Copyright.txt", dst="licenses", src=self._source_subfolder)
        else:
            self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.pdb")

    def package_info(self):
        aec_name = "aec"
        if self.settings.os == "Windows" and tools.Version(self.version) >= "1.0.6" and not self.options.shared:
            aec_name = "aec_static" 
        szip_name = "sz"
        if self.settings.os == "Windows":
            if tools.Version(self.version) >= "1.0.6":
                szip_name = "szip" if self.options.shared else "szip_static"
            elif self.options.shared:
                szip_name = "szip"
        self.cpp_info.libs = [aec_name, szip_name,]
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
