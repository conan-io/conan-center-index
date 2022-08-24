import os

from conans import ConanFile, tools, MSBuild, AutoToolsBuildEnvironment
from conan.errors import ConanInvalidConfiguration


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
               "with_libuv": [True, False, "deprecated"],
               "eventloop": ["syscall", "libuv", "gcd", "boost"]}
    default_options = {"fPIC": True,
                       "with_ssl": False,
                       "with_libuv": "deprecated",
                       "eventloop": "syscall"}
    exports_sources = "patches/**"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            self.options.eventloop = "libuv"

    def _minimum_compilers_version(self, cppstd):
        standards = {
            "14": {
                "Visual Studio": "15",
                "gcc": "5",
                "clang": "3.4",
                "apple-clang": "10",
            },
            "17": {
                "Visual Studio": "16",
                "gcc": "7",
                "clang": "6",
                "apple-clang": "10",
            },
        }
        return standards.get(cppstd) or {}

    @property
    def _cppstd(self):
        version = False
        if self.options.eventloop == "boost":
            version = "14"

        # OpenSSL wrapper of uSockets uses C++17 features.
        if self.options.with_ssl == "openssl":
            version = "17"

        return version

    def validate(self):
        if self.options.eventloop == "syscall" and self.settings.os == "Windows":
            raise ConanInvalidConfiguration("syscall is not supported on Windows")

        if self.options.eventloop == "gcd" and (self.settings.os != "Linux" or self.settings.compiler != "clang"):
            raise ConanInvalidConfiguration("eventloop=gcd is only supported on Linux with clang")

        if tools.Version(self.version) < "0.8.0" and self.options.eventloop not in ("syscall", "libuv", "gcd"):
            raise ConanInvalidConfiguration(f"eventloop={self.options.eventloop} is not supported with {self.name}/{self.version}")

        if tools.Version(self.version) >= "0.5.0" and self.options.with_ssl == "wolfssl":
            raise ConanInvalidConfiguration(f"with_ssl={self.options.with_ssl} is not supported with {self.name}/{self.version}. https://github.com/uNetworking/uSockets/issues/147")

        if self.options.with_ssl == "wolfssl" and not self.options["wolfssl"].opensslextra:
            raise ConanInvalidConfiguration("wolfssl needs opensslextra option enabled for usockets")

        if not self.options.with_libuv and self.settings.os == "Windows":
            raise ConanInvalidConfiguration("uSockets in Windows uses libuv by default. After 0.8.0, you can choose boost.asio by eventloop=boost.")

        cppstd = self._cppstd
        if not cppstd:
            return

        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, cppstd)

        minimum_version = self._minimum_compilers_version(cppstd).get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("{} requires C++{}, which your compiler does not support.".format(self.name, cppstd))
        else:
            self.output.warn("{0} requires C++{1}. Your compiler is unknown. Assuming it supports C++{1}.".format(self.name, cppstd))

    def configure(self):
        if bool(self._cppstd) == False:
            del self.settings.compiler.cppstd
            del self.settings.compiler.libcxx

        if self.options.with_libuv != "deprecated":
            self.output.warn("with_libuv is deprecated, use 'eventloop' instead.")
            if self.options.with_libuv == True:
                self.options.eventloop = "libuv"
            else:
                self.options.eventloop = "syscall"

    def requirements(self):
        if self.options.with_ssl == "openssl":
            self.requires("openssl/1.1.1q")
        elif self.options.with_ssl == "wolfssl":
            self.requires("wolfssl/5.3.0")

        if self.options.eventloop == "libuv":
            self.requires("libuv/1.44.1")
        elif self.options.eventloop == "gcd":
            self.requires("libdispatch/5.3.2")
        elif self.options.eventloop == "boost":
            self.requires("boost/1.79.0")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("uSockets-%s" % self.version, self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def _build_msvc(self):
        with tools.chdir(os.path.join(self._source_subfolder)):
            msbuild = MSBuild(self)
            msbuild.build(project_file="uSockets.vcxproj", platforms={"x86": "Win32"})

    def _build_configure(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.fpic = self.options.get_safe("fPIC", False)
        with tools.chdir(self._source_subfolder):
            args = []
            if self.options.with_ssl == "openssl":
                args.append("WITH_OPENSSL=1")
            elif self.options.with_ssl == "wolfssl":
                args.append("WITH_WOLFSSL=1")

            if self.options.eventloop == "libuv":
                args.append("WITH_LIBUV=1")
            elif self.options.eventloop == "gcd":
                args.append("WITH_GCD=1")
            elif self.options.eventloop == "boost":
                args.append("WITH_ASIO=1")

            args.extend("{}={}".format(key, value) for key, value in autotools.vars.items())
            autotools.make(target="default", args=args)

    def build(self):
        self._patch_sources()
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

    def package_id(self):
        # Deprecated options
        del self.info.options.with_libuv

    def package_info(self):
        self.cpp_info.libs = ["uSockets"]

        if self.options.with_ssl == "openssl":
            self.cpp_info.defines.append("LIBUS_USE_OPENSSL")
        elif self.options.with_ssl == "wolfssl":
            self.cpp_info.defines.append("LIBUS_USE_WOLFSSL")
        else:
            self.cpp_info.defines.append("LIBUS_NO_SSL")

        if self.options.eventloop == "libuv":
            self.cpp_info.defines.append("LIBUS_USE_LIBUV")
        elif self.options.eventloop == "gcd":
            self.cpp_info.defines.append("LIBUS_USE_GCD")
        elif self.options.eventloop == "boost":
            self.cpp_info.defines.append("LIBUS_USE_ASIO")
