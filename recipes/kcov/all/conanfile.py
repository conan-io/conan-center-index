import os
from shutil import rmtree, move
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class KcovConan(ConanFile):
    name = "kcov"
    license = "GPL-2.0"
    url = "https://github.com/conan-io/conan-center-index/"
    homepage = "http://simonkagstrom.github.io/kcov/index.html"
    description = "Code coverage tool for compiled programs, Python and Bash\
        which uses debugging information to collect and report data without\
            special compilation options"
    topics = ("coverage", "linux", "debug")
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "CMakeLists.txt", "patches/**"
    requires = ["zlib/1.2.11",
                "libiberty/9.1.0",
                "libcurl/7.64.1",
                "elfutils/0.180"]
    generators = "cmake"

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def configure(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration(
                "kcov can not be built by Visual Studio.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder)
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder)
        cmake.install()
        licdir = os.path.join(self.package_folder, "share", "doc", "kcov")
        move(licdir, os.path.join(self.package_folder, "licenses"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}"
                         .format(bindir))
        self.env_info.PATH.append(bindir)
