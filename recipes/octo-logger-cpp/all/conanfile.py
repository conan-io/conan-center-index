from conans import CMake
from conans import ConanFile
from conans import tools


class OctoLoggerCPPConan(ConanFile):
    name = "octo-logger-cpp"
    license = "MIT"
    url = "https://github.com/ofiriluz/octo-logger-cpp"
    homepage = "https://github.com/ofiriluz/octo-logger-cpp"
    description = "Octo logger library"
    topics = ("logging", "cpp")
    author = "Ofir Iluz"
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def requirements(self):
        self.requires("catch2/3.1.0")
        self.requires("fmt/9.0.0")
        self.requires("trompeloeil/42")

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder)
        cmake.build()
        cmake.test()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = CMake(self)
        cmake.install(build_dir=self._build_subfolder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
