import os

from conans import ConanFile, tools, MSBuild
from conans.errors import ConanInvalidConfiguration


class UsocketsConan(ConanFile):
    name = "usockets"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Miniscule cross-platform eventing, networking & crypto for async applications"
    license = "Apache-2.0"
    homepage = "https://github.com/uNetworking/uSockets"
    topics = ("conan", "socket", "network", "web")
    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False],
               "with_openssl": [True, False]}
    default_options = {"fPIC": True, 'with_openssl': False}
    generators = "cmake"
    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.compiler == "Visual Studio" and self.options.with_openssl:
            raise ConanInvalidConfiguration("Windows SSL build is not supported")
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/1.1.1g")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("usockets-%s" % self.version, self._source_subfolder)


    def _build_msvc(self):
        with tools.chdir(os.path.join(self._source_subfolder)):
            msbuild = MSBuild(self)
            msbuild.build(project_file="uSockets.vcxproj")

    def _build_configure(self):
        make_program = tools.get_env("CONAN_MAKE_PROGRAM", tools.which("make"))
        with tools.chdir(self._source_subfolder):
            args = []
            if self.options.with_openssl:
                args.append("WITH_OPENSSL=1")
                tools.replace_in_file("Makefile",
                                      "override CFLAGS += -DLIBUS_USE_OPENSSL",
                                      "override CFLAGS += -DLIBUS_USE_OPENSSL " +
                                      ' '.join(['-I'+s for s in self.deps_cpp_info['openssl'].include_paths])
                                     )
                tools.replace_in_file("Makefile",
                                      "override LDFLAGS += -lssl -lcrypto",
                                      "override LDFLAGS += " +
                                      ' '.join(['-L'+s for s in self.deps_cpp_info['openssl'].libdirs]) + " -lssl -lcrypto"
                                     )
            self.run("%s %s" % (' '.join(args), make_program))

    def build(self):
        if self.settings.compiler == "Visual Studio":
            self._build_msvc()
        else:
            self._build_configure()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.h", src=os.path.join(self._source_subfolder, "src"), dst="include", keep_path=True)
        self.copy(pattern="*.a", src=os.path.join(self._source_subfolder), dst="lib", keep_path=False)
        # drop internal headers
        tools.rmdir(os.path.join(self.package_folder, "include", "internal"))
        # fix library name
        if self.settings.compiler != "Visual Studio":
            os.rename(os.path.join(self.package_folder, "lib", "uSockets.a"), os.path.join(self.package_folder, "lib", "libuSockets.a"))

    def package_info(self):
        self.cpp_info.libs = ["uSockets"]
        if self.options.with_openssl:
            self.cpp_info.defines.append("LIBUS_USE_OPENSSL")
        else:
            self.cpp_info.defines.append("LIBUS_NO_SSL")
