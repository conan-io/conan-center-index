from conans import ConanFile, AutoToolsBuildEnvironment, tools, MSBuild
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


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

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def config_options(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def configure(self):
        if not self._is_msvc and self.settings.os not in ["Linux", "FreeBSD", "Macos"]:
            raise ConanInvalidConfiguration("sassc supports only Linux, FreeBSD, Macos and Windows Visual Studio at this time, contributions are welcomed")

    def requirements(self):
        self.requires("libsass/3.6.4")

    def build_requirements(self):
        if not self._is_msvc:
            self.build_requires("libtool/2.4.6")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        tools.replace_in_file(
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
        with tools.chdir(self._source_subfolder):
            if self._is_msvc:
                self._build_msbuild()
            else:
                self.run("{} -fiv".format(tools.get_env("AUTORECONF")), run_environment=True)
                tools.save(path="VERSION", content="%s" % self.version)
                autotools = self._configure_autotools()
                autotools.make()

    def package(self):
        with tools.chdir(self._source_subfolder):
            if self._is_msvc:
                self.copy("*.exe", dst="bin", src=os.path.join(self._source_subfolder, "bin"), keep_path=False)
            else:
                autotools = self._configure_autotools()
                autotools.install()
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
