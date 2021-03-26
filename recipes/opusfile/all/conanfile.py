from conans import ConanFile, MSBuild, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os


class OpusFileConan(ConanFile):
    name = "opusfile"
    description = "stand-alone decoder library for .opus streams"
    topics = ("conan", "opus", "opusfile", "audio", "decoder", "decoding", "multimedia", "sound")
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
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self._is_msvc and self.options.shared:
            raise ConanInvalidConfiguration("Opusfile doesn't support building as shared with Visual Studio")

    def requirements(self):
        self.requires("ogg/1.3.4")
        self.requires("opus/1.3.1")
        if self.options.http:
            self.requires("openssl/1.1.1i")

    def build_requirements(self):
        if not self._is_msvc:
            # FIXME: needs libtool for `autoreconf`, but the `configure.ac` file uses `m4_esyscmd` with bash code as argument.
            # Looks like this does not work with a MSVC-built m4.
            # self.build_requires("libtool/2.4.6")
            if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/20200517")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

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
            tools.patch(**patch)
        if self._is_msvc:
            self._build_vs()
        else:
            with tools.chdir(self._source_subfolder):
                self.run("./autogen.sh", win_bash=tools.os_info.is_windows, run_environment=True)
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
            tools.rmdir(os.path.join(self.package_folder, "share"))
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            os.remove(os.path.join(self.package_folder, "lib", "libopusfile.la"))
            os.remove(os.path.join(self.package_folder, "lib", "libopusurl.la"))

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
