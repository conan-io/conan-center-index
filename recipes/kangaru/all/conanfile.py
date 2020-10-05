from conans import ConanFile, tools, CMake
import os


class KangaruConan(ConanFile):
    name = "kangaru"
    description = "A dependency injection container for C++11, C++14 and later"
    license = "MIT"
    topics = ("conan", "gracicot", "kangaru",
              "DI", "IoC", "inversion of control")
    homepage = "https://github.com/gracicot/kangaru/wiki"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {"reverse_destruction": [True, False],
               "no_exception": [True, False]}
    default_options = {"reverse_destruction": True,
                       "no_exception": False}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def package_id(self):
        self.info.settings.clear()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["KANGARU_REVERSE_DESTRUCTION"] = self.options.reverse_destruction
        self._cmake.definitions["KANGARU_NO_EXCEPTION"] = self.options.no_exception
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib"))
        self.copy(os.path.join(self._source_subfolder, "LICENSE"), "licenses")
