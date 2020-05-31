from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
from conans.errors import ConanInvalidConfiguration
import os


class LibId3TagConan(ConanFile):
    name = "libid3tag"
    description = "ID3 tag manipulation library."
    topics = ("conan", "mad", "id3", "MPEG", "audio", "decoder")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.underbit.com/products/mad/"
    license = "GPL-2.0-or-later"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    requires = "zlib/1.2.11"
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self._is_msvc and self.options.shared:
            raise ConanInvalidConfiguration(
                "libid3tag does not support shared library for MSVC"
            )

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio" or (
            self.settings.compiler == "clang" and self.settings.os == "Windows"
        )

    def build(self):
        if self._is_msvc:
            self._build_msvc()
        else:
            self._build_configure()

    def _build_msvc(self):
        kwargs = {}
        with tools.chdir(os.path.join(self._source_subfolder, "msvc++")):
            # cl : Command line error D8016: '/ZI' and '/Gy-' command-line options are incompatible
            tools.replace_in_file("libid3tag.dsp", "/ZI ", "")
            if self.settings.compiler == "clang":
                tools.replace_in_file("libid3tag.dsp", "CPP=cl.exe", "CPP=clang-cl.exe")
                tools.replace_in_file("libid3tag.dsp", "RSC=rc.exe", "RSC=llvm-rc.exe")
                kwargs["toolset"] = "ClangCl"
            if self.settings.arch == "x86_64":
                tools.replace_in_file("libid3tag.dsp", "Win32", "x64")
            with tools.vcvars(self.settings):
                self.run("devenv libid3tag.dsp /upgrade")
            msbuild = MSBuild(self)
            msbuild.build(project_file="libid3tag.vcxproj", **kwargs)

    def _build_configure(self):
        with tools.chdir(self._source_subfolder):
            if self.options.shared:
                args = ["--disable-static", "--enable-shared"]
            else:
                args = ["--disable-shared", "--enable-static"]
            env_build = AutoToolsBuildEnvironment(self)
            env_build.configure(args=args)
            env_build.make()
            env_build.install()
            la = os.path.join(self.package_folder, "lib", "libid3tag.la")
            if os.path.isfile(la):
                os.unlink(la)

    def package(self):
        self.copy("COPYRIGHT", dst="licenses", src=self._source_subfolder)
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        self.copy("CREDITS", dst="licenses", src=self._source_subfolder)
        if self._is_msvc:
            self.copy(
                pattern="*.lib", dst="lib", src=self._source_subfolder, keep_path=False
            )
            self.copy(pattern="id3tag.h", dst="include", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = ["libid3tag" if self._is_msvc else "id3tag"]
