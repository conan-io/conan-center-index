from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, chdir, collect_libs, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
from conans import AutoToolsBuildEnvironment, MSBuild, tools
import os

required_conan_version = ">=1.53.0"


class LibStudXmlConan(ConanFile):
    name = "libstudxml"
    description = "A streaming XML pull parser and streaming XML serializer implementation for modern, standard C++."
    topics = ("xml", "xml-parser", "serialization")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.codesynthesis.com/projects/libstudxml/"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
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

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        pass

    def requirements(self):
        self.requires("expat/2.5.0", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.info.settings.compiler == "Visual Studio" and Version(self.info.settings.compiler.version) < "9":
            raise ConanInvalidConfiguration(f"Visual Studio {self.info.settings.compiler.version} is not supported.")

    def build_requirements(self):
        if not is_msvc(self):
            self.tool_requires("gnu-config/cci.20210814")
            self.tool_requires("libtool/2.4.7")
            if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
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

    @property
    def _vc_ver(self):
        if self.settings.compiler == "Visual Studio":
            return str(Version(self.settings.compiler.version).major)
        elif self.settings.compiler == "msvc":
            return {
                "170": "11",
                "180": "12",
                "190": "14",
                "191": "15",
                "192": "16",
                "193": "17",
            }[str(self.settings.compiler.version)]
        return None

    def _build_vs(self):
        vc_ver = int(self._vc_ver)
        sln_path = None
        def get_sln_path():
            return os.path.join(self.source_folder, self._source_subfolder, f"libstudxml-vc{vc_ver}.sln")

        sln_path = get_sln_path()
        while not os.path.exists(sln_path):
            vc_ver -= 1
            sln_path = get_sln_path()

        proj_path = os.path.join(self.source_folder, self._source_subfolder, "xml", f"libstudxml-vc{vc_ver}.vcxproj")

        if not self.options.shared:
            replace_in_file(self, proj_path, "DynamicLibrary", "StaticLibrary")
            replace_in_file(self, proj_path, "LIBSTUDXML_DYNAMIC_LIB", "LIBSTUDXML_STATIC_LIB")

        msbuild = MSBuild(self)
        msbuild.build(sln_path, platforms={"x86": "Win32"})

    def _build_autotools(self):
        for gnu_config in [
            self.conf.get("user.gnu-config:config_guess", check_type=str),
            self.conf.get("user.gnu-config:config_sub", check_type=str),
        ]:
            if gnu_config:
                copy(
                    self,
                    os.path.basename(gnu_config),
                    src=os.path.dirname(gnu_config),
                    dst=os.path.join(self.source_folder, self._source_subfolder, "config"),
                )

        if self.settings.compiler.get_safe("libcxx") == "libc++":
            # libc++ includes a file called 'version', and since libstudxml adds source_subfolder as an
            # include dir, libc++ ends up including their 'version' file instead, causing a compile error
            rm(self, "version", os.path.join(self.source_folder, self._source_subfolder))

        with chdir(self, os.path.join(self.source_folder, self._source_subfolder)):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)

        autotools = self._configure_autotools()
        autotools.make()

    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            self._build_vs()
        else:
            self._build_autotools()

    def package(self):
        copy(self, "LICENSE", src=os.path.join(self.source_folder, self._source_subfolder), dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
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
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libstudxml")
        self.cpp_info.libs = collect_libs(self)

        # If built with makefile, static library mechanism is provided by their buildsystem already
        if is_msvc(self) and not self.options.shared:
            self.cpp_info.defines = ["LIBSTUDXML_STATIC_LIB=1"]
