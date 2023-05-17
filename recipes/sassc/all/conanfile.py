from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, replace_in_file, chdir, save
from conan.tools.microsoft import is_msvc
from conans import AutoToolsBuildEnvironment, tools, MSBuild
import os

required_conan_version = ">=1.47.0"


class SasscConan(ConanFile):
    name = "sassc"
    license = "MIT"
    homepage = "https://sass-lang.com/libsass"
    url = "https://github.com/conan-io/conan-center-index"
    description = "libsass command line driver"
    topics = ("Sass", "sassc", "compiler")
    settings = "os", "compiler", "build_type", "arch"
    generators = "visual_studio"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def package_id(self):
        del self.info.settings.compiler

    def validate(self):
        if not is_msvc(self) and self.info.settings.os not in ["Linux", "FreeBSD", "Macos"]:
            raise ConanInvalidConfiguration("sassc supports only Linux, FreeBSD, Macos and Windows Visual Studio at this time, contributions are welcomed")

    def requirements(self):
        self.requires("libsass/3.6.5")

    def build_requirements(self):
        if not is_msvc(self):
            self.tool_requires("libtool/2.4.7")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        replace_in_file(self,
            os.path.join(self.build_folder, self._source_subfolder, "win", "sassc.vcxproj"),
            "$(LIBSASS_DIR)\\win\\libsass.targets",
            os.path.join(self.build_folder, "conanbuildinfo.props"))

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        self._autotools.configure(args=["--disable-tests"])
        return self._autotools

    def _build_msbuild(self):
        msbuild = MSBuild(self)
        platforms = {
            "x86": "Win32",
            "x86_64": "Win64"
        }
        msbuild.build("win/sassc.sln", platforms=platforms)

    def build(self):
        self._patch_sources()
        with chdir(self, self._source_subfolder):
            if is_msvc(self):
                self._build_msbuild()
            else:
                self.run("{} -fiv".format(tools.get_env("AUTORECONF")), run_environment=True)
                save(self, path="VERSION", content=f"{self.version}")
                autotools = self._configure_autotools()
                autotools.make()

    def package(self):
        with chdir(self, self._source_subfolder):
            if is_msvc(self):
                self.copy("*.exe", dst="bin", src=os.path.join(self._source_subfolder, "bin"), keep_path=False)
            else:
                autotools = self._configure_autotools()
                autotools.install()
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        bin_folder = os.path.join(self.package_folder, "bin")
        # TODO: Legacy, to be removed on Conan 2.0
        self.env_info.PATH.append(bin_folder)
