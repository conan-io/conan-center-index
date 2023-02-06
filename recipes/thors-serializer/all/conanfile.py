from conan import ConanFile
from conans import AutoToolsBuildEnvironment
from conans import tools

class ThorsSerializerConan(ConanFile):
    name        = "thors-serializer"
    author      = "Martin York (Aka Loki Astari) Martin.York@gmail.com"
    url         = "git@github.com:Loki-Astari/ThorsSerializer.git"
    license     = "MIT"
    description = """No Code Serialization Library.
                     Supports: JSON YAML BSON"""
    settings    = "cppstd", "os", "compiler", "build_type", "arch"
    scm         = {
        "type"      : "git",
        "url"       : "git@github.com:Loki-Astari/ThorsSerializer.git",
        "revision"  : "426ba1018f03b77594e6202c4352b0e1a9a150a1"
    }
    requires = "libyaml/0.2.5", "boost/1.81.0", "magic_enum/0.8.2"
    cppminimum = 17

    def configure(self):
        if not self.settings.cppstd:
            self.settings.cppstd = self.cppminimum

    def validate(self):
        tools.valid_min_cppstd(self, self.cppminimum)

    def build_id(self):
        self.info_build.settings.build_type = "Any"

    def build(self):
        atools = AutoToolsBuildEnvironment(self)
        atools.configure(args=["--disable-vera", f"--with-standard={self.settings.cppstd}"])
        atools.make()

    def package(self):
        atools = AutoToolsBuildEnvironment(self)
        atools.install()

    def package_info(self):
        self.cpp_info.libs = [ f"ThorsLogging{self.settings.cppstd}", f"ThorSerialize{self.settings.cppstd}" ]
