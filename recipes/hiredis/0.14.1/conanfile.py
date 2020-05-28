from conans import AutoToolsBuildEnvironment, ConanFile, tools

from os import rename
from os.path import join


class HiredisConan(ConanFile):
    name = "hiredis"

    description = "Minimalistic C client for Redis >= 1.2"
    topics = "conan", "c", "redis"

    license = "BSD 3-Clause \"New\" or \"Revised\" License"
    settings = "os", "arch", "compiler", "build_type"

    homepage = "https://github.com/redis/hiredis"
    url = "https://github.com/conan-io/conan-center-index"

    options = {
        "fPIC": [True, False],
        "shared": [True, False]
    }
    default_options = {
        "fPIC": True,
        "shared": True
    }

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = self.name + "-" + self.version
        rename(extracted_folder, "src")

    def build(self):
        # settings
        isWindows = self.settings.os == "Windows"

        # update makefile
        makefile = join(self.source_folder, "src", "Makefile")
        tools.replace_in_file(makefile, "-fPIC ", "", strict=False)

        with tools.chdir(join(self.source_folder, "src")):
            autoTools = AutoToolsBuildEnvironment(self, win_bash=isWindows)
            autoTools.make()

    def package(self):
        # settings
        isWindows = self.settings.os == "Windows"

        with tools.chdir(join(self.source_folder, "src")):
            autoTools = AutoToolsBuildEnvironment(self, win_bash=isWindows)
            autoTools.install(vars={
                "DESTDIR": join(self.build_folder),
                "PREFIX": ""
            })

        # headers
        self.copy("*.h", dst="include/hiredis", src="include/hiredis")

        # libs
        if self.options.shared:
            self.copy("*.dylib", dst="lib", keep_path=False)
            self.copy("*.so", dst="lib", keep_path=False)
        else:
            self.copy("*.a", dst="lib", keep_path=False)

        # licenses
        self.copy("COPYING", dst="licenses", src="src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
