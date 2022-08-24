from conans import CMake, ConanFile, tools
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
    generators = "cmake", "cmake_find_package"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        self.requires("boost/1.75.0")

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version][0])
        os.rename("boostdep-boost-{}".format(self.version), self._source_subfolder)
        license_info = self.conan_data["sources"][self.version][1]
        tools.files.download(self, filename=os.path.basename(license_info["url"]), **license_info)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["Boost_USE_STATIC_LIBS"] = not self.options["boost"].shared
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE*", dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.deps_env_info.PATH.append(bin_path)
