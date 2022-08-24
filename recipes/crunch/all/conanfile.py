import os
import glob
from conans import ConanFile, tools, CMake, MSBuild
from conan.errors import ConanInvalidConfiguration


class CrunchConan(ConanFile):
    name = "crunch"
    description = "Advanced DXTc texture compression and transcoding library"
    homepage = "https://github.com/BinomialLLC/crunch"
    topics = ("conan", "crunch", "DXTc", "texture", "compression", "decompression", "transcoding")
    url = "https://github.com/conan-io/conan-center-index"
    license = "Zlib"
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.os not in ["Windows", "Linux"]:
            raise ConanInvalidConfiguration("Crunch is not supported on {}.".format(self.settings.os))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob('crunch-*/')[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("license.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: %s' % bin_path)
        self.env_info.path.append(bin_path)
