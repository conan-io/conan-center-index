from conans import ConanFile, AutoToolsBuildEnvironment, MSBuild, tools
from conan.errors import ConanInvalidConfiguration
import os
import shutil

required_conan_version = ">=1.33.0"


class LibStudXmlConan(ConanFile):
    name = "libstudxml"
    description = "A streaming XML pull parser and streaming XML serializer implementation for modern, standard C++."
    topics = ("xml", "xml-parser", "serialization")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.codesynthesis.com/projects/libstudxml/"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"

    exports_sources = "patches/*"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("expat/2.4.1")

    def validate(self):
        if self.settings.compiler == "Visual Studio":
            if tools.Version(self.settings.compiler.version) < "9":
                raise ConanInvalidConfiguration("Visual Studio {} is not supported.".format(self.settings.compiler.version))

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self.settings.compiler != "Visual Studio":
            self.build_requires("gnu-config/cci.20201022")
            self.build_requires("libtool/2.4.6")
            if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if not self._autotools:
            args = ["--with-external-expat"]
            if self.options.shared:
                args.extend(["--enable-shared", "--disable-static"])
            else:
                args.extend(["--disable-shared", "--enable-static"])

            self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            self._autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self._autotools

    def _build_vs(self):
        vc_ver = int(tools.Version(self.settings.compiler.version).major)
        sln_path = None
        def get_sln_path():
            return os.path.join(self._source_subfolder, "libstudxml-vc{}.sln".format(vc_ver))

        sln_path = get_sln_path()
        while not os.path.exists(sln_path):
            vc_ver -= 1
            sln_path = get_sln_path()

        proj_path = os.path.join(self._source_subfolder, "xml", "libstudxml-vc{}.vcxproj".format(vc_ver))

        if not self.options.shared:
            tools.files.replace_in_file(self, proj_path, "DynamicLibrary", "StaticLibrary")
            tools.files.replace_in_file(self, proj_path, "LIBSTUDXML_DYNAMIC_LIB", "LIBSTUDXML_STATIC_LIB")

        msbuild = MSBuild(self)
        msbuild.build(sln_path, platforms={"x86": "Win32"})

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def _build_autotools(self):
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB,
                    os.path.join(self._source_subfolder, "config", "config.sub"))
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS,
                    os.path.join(self._source_subfolder, "config", "config.guess"))

        if self.settings.compiler.get_safe("libcxx") == "libc++":
            # libc++ includes a file called 'version', and since libstudxml adds source_subfolder as an
            # include dir, libc++ ends up including their 'version' file instead, causing a compile error
            tools.files.rm(self, self._source_subfolder, "version")

        with tools.files.chdir(self, self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)

        autotools = self._configure_autotools()
        autotools.make()

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

        if self.settings.compiler == "Visual Studio":
            self._build_vs()
        else:
            self._build_autotools()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        if self.settings.compiler == "Visual Studio":
            self.copy("xml/value-traits", dst="include", src=self._source_subfolder)
            self.copy("xml/serializer", dst="include", src=self._source_subfolder)
            self.copy("xml/qname", dst="include", src=self._source_subfolder)
            self.copy("xml/parser", dst="include", src=self._source_subfolder)
            self.copy("xml/forward", dst="include", src=self._source_subfolder)
            self.copy("xml/exception", dst="include", src=self._source_subfolder)
            self.copy("xml/content", dst="include", src=self._source_subfolder)
            self.copy("xml/*.ixx", dst="include", src=self._source_subfolder)
            self.copy("xml/*.txx", dst="include", src=self._source_subfolder)
            self.copy("xml/*.hxx", dst="include", src=self._source_subfolder)
            self.copy("xml/*.h", dst="include", src=self._source_subfolder)

            suffix = ""
            if self.settings.arch == "x86_64":
                suffix = "64"
            if self.options.shared:
                self.copy("*.lib", dst="lib", src=os.path.join(self._source_subfolder, "lib" + suffix))
                self.copy("*.dll", dst="bin", src=os.path.join(self._source_subfolder, "bin" + suffix))
            else:
                self.copy("*.lib", dst="lib", src=os.path.join(self._source_subfolder, "bin" + suffix))
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.files.rm(self, os.path.join(self.package_folder, "lib"), "libstudxml.la")
            tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.names["pkg_config"] = "libstudxml"

        # If built with makefile, static library mechanism is provided by their buildsystem already
        if self.settings.compiler == "Visual Studio" and not self.options.shared:
            self.cpp_info.defines = ["LIBSTUDXML_STATIC_LIB=1"]
