from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class BoostDepConan(ConanFile):
    name = "boostdep"
    settings = "os", "arch", "compiler", "build_type"
    description = "A tool to create Boost module dependency reports"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/boostorg/boostdep"
    license = "BSL-1.0"
    topics = ("conan", "boostdep", "dependency", "tree")
    exports_sources = "CMakeLists.txt"
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        self.requires("boost/{}".format(self.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version][0])
        os.rename("boostdep-boost-{}".format(self.version), self._source_subfolder)
        license_info = self.conan_data["sources"][self.version][1]
        tools.download(filename=os.path.basename(license_info["url"]), **license_info)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        if self.settings.build_type != "Release":
            raise ConanInvalidConfiguration("Only Release built_type supported")
        if self.settings.compiler == "Visual Studio" and self.settings.compiler.runtime != "MT":
            raise ConanInvalidConfiguration("Only MT runtime supported")

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE*", dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_id(self):
        del self.info.settings

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.deps_env_info.PATH.append(bin_path)
