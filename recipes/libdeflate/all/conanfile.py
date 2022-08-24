from conans import ConanFile, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment, tools
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.33.0"


class LibdeflateConan(ConanFile):
    name = "libdeflate"
    description = "Heavily optimized library for DEFLATE/zlib/gzip compression and decompression."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ebiggers/libdeflate"
    topics = ("libdeflate", "compression", "decompression", "deflate", "zlib", "gzip")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_clangcl(self):
        return self.settings.compiler == "clang" and self.settings.os == "Windows"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not is_msvc(self) and \
           not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _build_msvc(self):
        with tools.chdir(self._source_subfolder):
            with tools.vcvars(self):
                with tools.environment_append(VisualStudioBuildEnvironment(self).vars):
                    target = "libdeflate.dll" if self.options.shared else "libdeflatestatic.lib"
                    self.run("nmake /f Makefile.msc {}".format(target))

    def _build_make(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        with tools.chdir(self._source_subfolder):
            autotools.make()

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if is_msvc(self) or self._is_clangcl:
            self._build_msvc()
        else:
            self._build_make()

    def _package_windows(self):
        self.copy("libdeflate.h", dst="include", src=self._source_subfolder)
        if self.options.shared:
            self.copy("*deflate.lib", dst="lib", src=self._source_subfolder)
            self.copy("*deflate.dll", dst="bin", src=self._source_subfolder)
        else:
            self.copy("*deflatestatic.lib", dst="lib", src=self._source_subfolder)

    def _package_make(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        with tools.chdir(self._source_subfolder):
            autotools.install(args=["PREFIX={}".format(self.package_folder)])
        tools.rmdir(os.path.join(self.package_folder, "bin"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(
            os.path.join(self.package_folder, "lib"),
            "*.a" if self.options.shared else "*.[so|dylib]*",
        )

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        if self.settings.os == "Windows":
            self._package_windows()
        else:
            self._package_make()

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libdeflate")
        prefix = "lib" if self.settings.os == "Windows" else ""
        suffix = "static" if self.settings.os == "Windows" and not self.options.shared else ""
        self.cpp_info.libs = ["{0}deflate{1}".format(prefix, suffix)]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines = ["LIBDEFLATE_DLL"]
