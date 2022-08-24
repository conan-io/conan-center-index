from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"

class TinyAlsaConan(ConanFile):
    name = "tinyalsa"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tinyalsa/tinyalsa"
    topics = ("tiny", "alsa", "sound", "audio", "tinyalsa")
    description = "A small library to interface with ALSA in the Linux kernel"
    exports_sources = ["patches/*",]
    options = {"shared": [True, False], "with_utils": [True, False]}
    default_options = {'shared': False, 'with_utils': False}
    settings = "os", "compiler", "build_type", "arch"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("{} only works for Linux.".format(self.name))

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        with tools.chdir(self._source_subfolder):
            env_build = AutoToolsBuildEnvironment(self)
            env_build.make()

    def package(self):
        self.copy("NOTICE", dst="licenses", src=self._source_subfolder)

        with tools.chdir(self._source_subfolder):
            env_build = AutoToolsBuildEnvironment(self)
            env_build_vars = env_build.vars
            env_build_vars['PREFIX'] = self.package_folder
            env_build.install(vars=env_build_vars)

        tools.rmdir(os.path.join(self.package_folder, "share"))

        if not self.options.with_utils:
            tools.rmdir(os.path.join(self.package_folder, "bin"))

        with tools.chdir(os.path.join(self.package_folder, "lib")):
            files = os.listdir()
            for f in files:
                if (self.options.shared and f.endswith(".a")) or (not self.options.shared and not f.endswith(".a")):
                    os.unlink(f)

    def package_info(self):
        self.cpp_info.libs = ["tinyalsa"]
        if tools.Version(self.version) >= "2.0.0":
            self.cpp_info.system_libs.append("dl")
        if self.options.with_utils:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info('Appending PATH environment variable: %s' % bin_path)
            self.env_info.path.append(bin_path)
