from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration

import os


class XtrConan(ConanFile):
    name = "xtr"
    description = \
        "C++ Logging Library for Low-latency or Real-time Environments"
    topics = ("xtr", "logging", "logger")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/choll/xtr"
    # 8.0.0 is excluded due to https://github.com/fmtlib/fmt/issues/2377
    requires = "fmt/[>=6.0.0 < 8.0.0 || > 8.0.0]"
    license = "MIT"
    settings = {
        "os": ["Linux", "FreeBSD"],
        "compiler": ["gcc", "clang"],
        "build_type": None,
        "arch": ["x86_64"]}
    options = {
        "fPIC": [True, False],
        "enable_exceptions": [True, False],
        "enable_lto": [True, False]}
    default_options = {
        "fPIC": True,
        "enable_exceptions": True,
        "enable_lto": False}
    generators = "make"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True)

    def configure(self):
        minimal_cpp_standard = "20"
        if (self.settings.compiler.cppstd):
            tools.check_min_cppstd(self, minimal_cpp_standard)

        minimum_version = {"gcc": 10, "clang": 12}
        compiler = str(self.settings.compiler)
        version = tools.Version(self.settings.compiler.version)

        if version < minimum_version[compiler]:
            raise ConanInvalidConfiguration(
                "%s requires %s version %d or later"
                % (self.name, compiler, minimum_version[compiler]))

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        env_build_vars = autotools.vars
        # Conan uses LIBS, presumably following autotools conventions, while
        # the XTR makefile follows GNU make conventions and uses LDLIBS
        env_build_vars["LDLIBS"] = env_build_vars["LIBS"]
        # fPIC and Release/Debug/RelWithDebInfo etc are set via CXXFLAGS,
        # CPPFLAGS etc.
        env_build_vars["EXCEPTIONS"] = \
            str(int(bool(self.options.enable_exceptions)))
        env_build_vars["LTO"] = str(int(bool(self.options.enable_lto)))
        autotools.make(vars=env_build_vars)
        autotools.make(vars=env_build_vars, target="xtrctl")

    def package(self):
        self.copy("*.hpp", dst="include", src="include")
        self.copy("*/libxtr.a", dst="lib", src="build", keep_path=False)
        self.copy("*/xtrctl", dst="bin", src="build", keep_path=False)
        self.copy("LICENSE", "licenses")

    def package_info(self):
        self.cpp_info.libs = ["xtr"]
        self.cpp_info.system_libs = ["pthread"]
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.MANPATH.append(os.path.join(self.package_folder, "man"))
