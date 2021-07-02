import os

from conans import ConanFile, tools, MSBuild, AutoToolsBuildEnvironment
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
    exports_sources = "patches/**"

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
            self.requires("openssl/1.1.1k")
        elif self.options.with_ssl == "wolfssl":
            self.requires("wolfssl/4.6.0")
        if self.options.with_libuv:
            self.requires("libuv/1.41.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
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
            if self.options.with_libuv:
                args.append("WITH_LIBUV=1")
            # set CPPFLAGS, CFLAGS and LDFLAGS
            args.extend("{}={}".format(key, value) for key, value in autotools.vars.items())
            autotools.make(target="default", args=args)

    def build(self):
        if self.options.with_ssl == "wolfssl":
            if not self.options["wolfssl"].opensslextra:
                raise ConanInvalidConfiguration("wolfssl needs opensslextra option enabled for usockets")
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
