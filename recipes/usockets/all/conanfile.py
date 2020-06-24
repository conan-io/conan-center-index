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
               "with_ssl": [False, "openssl", "wolfssl"],
               "with_libuv": [True, False]}
    default_options = {"fPIC": True, "with_ssl": False, "with_libuv": True}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def requirements(self):
        if self.options.with_ssl == "openssl":
            self.requires("openssl/1.1.1g")
        elif self.options.with_ssl == "wolfssl":
            self.requires("wolfssl/4.4.0")
        if self.options.with_libuv:
            self.requires("libuv/1.38.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("uSockets-%s" % self.version, self._source_subfolder)

    def _build_msvc(self):
        with tools.chdir(os.path.join(self._source_subfolder)):
            tools.replace_in_file("uSockets.vcxproj",
                                  "<WindowsTargetPlatformVersion>10.0.17134.0</WindowsTargetPlatformVersion>", "")
            tools.replace_in_file("uSockets.vcxproj",
                                  "<ConfigurationType>DynamicLibrary</ConfigurationType>",
                                  "<ConfigurationType>StaticLibrary</ConfigurationType>")
            msbuild = MSBuild(self)
            msbuild.build(project_file="uSockets.vcxproj", platforms={"x86": "Win32"})

    def _build_configure(self):
        make_program = tools.get_env("CONAN_MAKE_PROGRAM", tools.which("make"))
        with tools.chdir(self._source_subfolder):
            additional_cflags = []
            additional_ldflags = []
            if self.options.with_ssl == "openssl":
                additional_cflags.extend(['-I'+s for s in self.deps_cpp_info['openssl'].include_paths])
                additional_ldflags.extend(['-L'+os.path.join(self.deps_cpp_info['openssl'].rootpath, s)
                                           for s in self.deps_cpp_info['openssl'].libdirs])
            if self.options.with_ssl == "wolfssl":
                additional_cflags.extend(['-I'+s for s in self.deps_cpp_info['wolfssl'].include_paths])
                additional_ldflags.extend(['-L'+os.path.join(self.deps_cpp_info['wolfssl'].rootpath, s)
                                           for s in self.deps_cpp_info['wolfssl'].libdirs])
            if self.options.with_libuv:
                additional_cflags.extend(['-I'+s for s in self.deps_cpp_info['libuv'].include_paths])
                additional_ldflags.extend(['-L'+os.path.join(self.deps_cpp_info['libuv'].rootpath, s)
                                           for s in self.deps_cpp_info['libuv'].libdirs])

            # set options for Makefile
            args = []
            if self.options.with_ssl == "openssl":
                args.append("WITH_OPENSSL=1")
            elif self.options.with_ssl == "wolfssl":
                args.append("WITH_WOLFSSL=1")
            if self.options.with_libuv:
                args.append("WITH_LIBUV=1")

            # set paths for dependencies
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
            # disable lto
            tools.replace_in_file("Makefile",
                                  " -flto",
                                  "")
            # fix output name
            tools.replace_in_file("Makefile",
                                  "rvs uSockets.a",
                                  "rvs libuSockets.a")
            self.run("%s %s" % (' '.join(args), make_program))

    def build(self):
        if self.options.with_ssl == "wolfssl":
            if not self.options["wolfssl"].opensslextra:
                raise ConanInvalidConfiguration("wolfssl needs opensslextra option enabled for usockets")
        if self.settings.compiler == "Visual Studio":
            self._build_msvc()
        else:
            self._build_configure()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.h", src=os.path.join(self._source_subfolder, "src"), dst="include", keep_path=True)
        self.copy(pattern="*.a", src=self._source_subfolder, dst="lib", keep_path=False)
        self.copy(pattern="*.lib", src=self._source_subfolder, dst="lib", keep_path=False)
        # drop internal headers
        tools.rmdir(os.path.join(self.package_folder, "include", "internal"))

    def package_info(self):
        self.cpp_info.libs = ["uSockets"]
        if self.options.with_ssl == "openssl":
            self.cpp_info.defines.append("LIBUS_USE_OPENSSL")
        elif self.options.with_ssl == "wolfssl":
            self.cpp_info.defines.append("LIBUS_USE_WOLFSSL")
        else:
            self.cpp_info.defines.append("LIBUS_NO_SSL")
        if self.options.with_libuv:
            self.cpp_info.defines.append("LIBUS_USE_LIBUV")
