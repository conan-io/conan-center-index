from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class GnConan(ConanFile):
    name = "gn"
    description = "GN is a meta-build system that generates build files for Ninja"
    license = "BSD-Google"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gn.googlesource.com/gn/"
    settings = "os", "arch", "compiler", "build_type"
    topics = ("conan", "ninja", "build", "google")
    exports_sources = ["patches/*.patch"]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _python_executable(self):
        return "python"

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 17)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder)

    def build_requirements(self):
        self.build_requires("ninja/1.10.1")

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

        gen = os.path.join(self._source_subfolder, "build", "gen.py")
        self.run("{} {} --out-path {}".format(self._python_executable,
                                              gen, self.build_folder))
        self.run("ninja -C {} -j {}".format(self.build_folder,
                                            tools.cpu_count()), run_environment=True)

    def package(self):
        gn_executable = "gn.exe" if self.settings.os == "Windows" else "gn"
        self.copy(pattern=gn_executable, dst="bin",
                  src=self.build_folder, keep_path=False)
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type
