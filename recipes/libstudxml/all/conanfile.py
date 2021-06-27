from conans import ConanFile, AutoToolsBuildEnvironment, MSBuild, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"

class LibStudXmlConan(ConanFile):
    name = "libstudxml"
    description = "A streaming XML pull parser and streaming XML serializer implementation for modern, standard C++."
    topics = ("xml", "xml-parser", "serialization")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.codesynthesis.com/projects/libstudxml/"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"

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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if not self._autotools:
            args = ["--with-extern-expat", "CXXFLAGS=\"-UNDEBUG\""]
            if self.options.shared:
                args.extend(["--enable-shared", "--disable-static"])
            else:
                args.extend(["--disable-shared", "--enable-static"])

            self._autotools = AutoToolsBuildEnvironment(self)
            self._autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self._autotools

    def _build_vs(self):
        if tools.Version(self.settings.compiler.version) < "9":
            raise ConanInvalidConfiguration("Visual Studio {} is not supported.".format(self.settings.compiler.version))

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
            tools.replace_in_file(proj_path, "DynamicLibrary", "StaticLibrary")
            tools.replace_in_file(proj_path, "LIBSTUDXML_DYNAMIC_LIB", "LIBSTUDXML_STATIC_LIB")

        msbuild = MSBuild(self)
        msbuild.build(sln_path, platforms={"x86": "Win32"})

    def build(self):
        if self.settings.compiler == "Visual Studio":
            self._build_vs()
        else:
            autotools = self._configure_autotools()
            autotools.make()

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
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "libstudxml.la")
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.names["pkg_config"] = "libstudxml"

        # If built with makefile, static library mechanism is provided by their buildsystem already
        if self.settings.compiler == "Visual Studio" and not self.options.shared:
            self.cpp_info.defines = ["LIBSTUDXML_STATIC_LIB=1"]
