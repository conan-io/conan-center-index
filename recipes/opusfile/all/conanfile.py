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
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = ["pkg_config"]
    requires = (
        "opus/1.3.1",
        "ogg/1.3.4",
        "openssl/1.1.1g"
    )
    exports = ["patches/*"]
    _autotools = None
    _source_subfolder = "source_subfolder"

    @property
    def _is_msvc(self):
        return self.settings.os == "Windows" and \
               self.settings.compiler == "Visual Studio"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self._is_msvc and self.options.shared:
            raise ConanInvalidConfiguration("Opusfile doesn't support building as shared with Visual Studio")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _build_vs(self):
        includedir = os.path.abspath(os.path.join(self._source_subfolder, "include"))
        with tools.chdir(os.path.join(self._source_subfolder, "win32", "VS2015")):
            msbuild = MSBuild(self)
            msbuild.build_env.include_paths.append(includedir)
            msbuild.build(project_file="opusfile.sln", targets=["opusfile"],
                          platforms={"x86": "Win32"},
                          upgrade_project=False)

    def _configure_autotools(self):
        if not self._autotools:
            with tools.chdir(self._source_subfolder):
                self.run("./autogen.sh", win_bash=tools.os_info.is_windows)
            args = []
            if self.options.shared:
                args.extend(["--disable-static", "--enable-shared"])
            else:
                args.extend(["--disable-shared", "--enable-static"])
            self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        if self._is_msvc:
            self._build_vs()
        else:
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
        self.cpp_info.libs = ["opusfile"]
        self.cpp_info.includedirs.append(os.path.join("include", "opus"))
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m", "dl", "pthread"]
