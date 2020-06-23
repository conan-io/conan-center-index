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
               "with_ssl": [False, "openssl"],
               "with_libuv": [True, False]}
    default_options = {"fPIC": True, 'with_ssl': False, 'with_libuv': True}
    generators = "cmake"
    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("Windows build is not supported by upstream")
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def requirements(self):
        if self.options.with_ssl == "openssl":
            self.requires("openssl/1.1.1g")
        if self.options.with_libuv:
            self.requires("libuv/1.38.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("usockets-%s" % self.version, self._source_subfolder)

    def _build_msvc(self):
        with tools.chdir(os.path.join(self._source_subfolder)):
            tools.replace_in_file("uSockets.vcxproj",
                                  "<WindowsTargetPlatformVersion>10.0.17134.0</WindowsTargetPlatformVersion>", "")
            msbuild = MSBuild(self)
            msbuild.build(project_file="uSockets.vcxproj")

    def _build_configure(self):
        make_program = tools.get_env("CONAN_MAKE_PROGRAM", tools.which("make"))
        with tools.chdir(self._source_subfolder):
            additional_cflags = []
            additional_ldflags = []
            if self.options.with_ssl == "openssl":
                additional_cflags.extend(['-I'+s for s in self.deps_cpp_info['openssl'].include_paths])
                additional_ldflags.extend(['-L'+os.path.join(self.deps_cpp_info['openssl'].rootpath, s)
                                           for s in self.deps_cpp_info['openssl'].libdirs])
            if self.options.with_libuv:
                additional_cflags.extend(['-I'+s for s in self.deps_cpp_info['libuv'].include_paths])
                additional_ldflags.extend(['-L'+os.path.join(self.deps_cpp_info['libuv'].rootpath, s)
                                           for s in self.deps_cpp_info['libuv'].libdirs])

            args = []
            if self.options.with_ssl == "openssl":
                args.append("WITH_OPENSSL=1")
            if self.options.with_libuv:
                args.append("WITH_LIBUV=1")
            tools.replace_in_file("Makefile",
                                  ".PHONY: examples",
                                  "override CFLAGS += " + ' '.join(additional_cflags) +
                                  "\n.PHONY: examples"
                                 )
            tools.replace_in_file("Makefile",
                                  ".PHONY: examples",
                                  "override LDFLAGS += " + ' '.join(additional_ldflags) +
                                  "\n.PHONY: examples\n"
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
        if self.options.with_ssl == "openssl":
            self.cpp_info.defines.append("LIBUS_USE_OPENSSL")
        else:
            self.cpp_info.defines.append("LIBUS_NO_SSL")
        if self.options.with_libuv:
            self.cpp_info.defines.append("LIBUS_USE_LIBUV")
