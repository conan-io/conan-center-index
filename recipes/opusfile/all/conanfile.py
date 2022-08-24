from conans import ConanFile, MSBuild, AutoToolsBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class OpusFileConan(ConanFile):
    name = "opusfile"
    description = "stand-alone decoder library for .opus streams"
    topics = ("opus", "opusfile", "audio", "decoder", "decoding", "multimedia", "sound")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xiph/opusfile"
    license = "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "http": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "http": True,
    }

    generators = "pkg_config"
    exports_sources = "patches/*"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self._is_msvc and self.options.shared:
            raise ConanInvalidConfiguration("Opusfile doesn't support building as shared with Visual Studio")

    def requirements(self):
        self.requires("ogg/1.3.5")
        self.requires("opus/1.3.1")
        if self.options.http:
            self.requires("openssl/1.1.1q")

    def build_requirements(self):
        if not self._is_msvc:
            self.build_requires("libtool/2.4.6")
            self.build_requires("pkgconf/1.7.4")
            if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _build_vs(self):
        includedir = os.path.abspath(os.path.join(self._source_subfolder, "include"))
        with tools.chdir(os.path.join(self._source_subfolder, "win32", "VS2015")):
            msbuild = MSBuild(self)
            build_type = str(self.settings.build_type)
            if not self.options.http:
                build_type += "-NoHTTP"
            msbuild.build_env.include_paths.append(includedir)
            msbuild.build(project_file="opusfile.sln", targets=["opusfile"],
                          platforms={"x86": "Win32"}, build_type=build_type,
                          upgrade_project=False)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-http={}".format(yes_no(self.options.http)),
            "--disable-examples",
        ]
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        if self._is_msvc:
            self._build_vs()
        else:
            with tools.chdir(self._source_subfolder):
                self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows, run_environment=True)
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        if self._is_msvc:
            include_folder = os.path.join(self._source_subfolder, "include")
            self.copy(pattern="*", dst=os.path.join("include", "opus"), src=include_folder)
            self.copy(pattern="*.dll", dst="bin", keep_path=False)
            self.copy(pattern="*.lib", dst="lib", keep_path=False)
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
            tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.components["libopusfile"].names["pkg_config"] = "opusfile"
        self.cpp_info.components["libopusfile"].libs = ["opusfile"]
        self.cpp_info.components["libopusfile"].includedirs.append(os.path.join("include", "opus"))
        self.cpp_info.components["libopusfile"].requires = ["ogg::ogg", "opus::opus"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.components["libopusfile"].system_libs = ["m", "dl", "pthread"]

        if self._is_msvc:
            if self.options.http:
                self.cpp_info.components["libopusfile"].requires.append("openssl::openssl")
        else:
            self.cpp_info.components["opusurl"].names["pkg_config"] = "opusurl"
            self.cpp_info.components["opusurl"].libs = ["opusurl"]
            self.cpp_info.components["opusurl"].requires = ["libopusfile"]
            if self.options.http:
                self.cpp_info.components["opusurl"].requires.append("openssl::openssl")
