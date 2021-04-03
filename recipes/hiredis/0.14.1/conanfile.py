from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration

import os


class HiredisConan(ConanFile):
    name = "hiredis"
    version = "0.14.1"

    description = "Minimalistic C client for Redis >= 1.2"
    topics = ("conan", "c", "redis")

    license = "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"

    homepage = "https://github.com/redis/hiredis"
    url = "https://github.com/conan-io/conan-center-index"

    options = {
        "fPIC": [True, False],
        "shared": [True, False]
    }
    default_options = {
        "fPIC": True,
        "shared": False
    }

    def _configure_autotools(self):
        autoTools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        return autoTools

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("hiredis %s is not supported on Windows." % self.version)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = self.name + "-" + self.version
        os.rename(extracted_folder, self._source_subfolder)

    def build(self):
        # update makefile
        makefile = os.path.join(self.source_folder, self._source_subfolder, "Makefile")
        tools.replace_in_file(makefile, "-fPIC ", "", strict=False)

        with tools.chdir(os.path.join(self.source_folder, self._source_subfolder)):
            autoTools = self._configure_autotools()
            autoTools.make()

    def package(self):
        with tools.chdir(os.path.join(self.source_folder, self._source_subfolder)):
            autoTools = self._configure_autotools()
            autoTools.install(vars={
                "DESTDIR": os.path.join(self.build_folder),
                "PREFIX": ""
            })

        # headers
        self.copy("*.h", dst=os.path.join("include", "hiredis"), src=os.path.join("include", "hiredis"))

        # libs
        if self.options.shared:
            self.copy("*.dylib", dst="lib", keep_path=False)
            self.copy("*.so", dst="lib", keep_path=False)
            self.copy("*.so.*", dst="lib", keep_path=False)
        else:
            self.copy("*.a", dst="lib", keep_path=False)

        # licenses
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
