from conan import ConanFile
from conan.tools.microsoft import is_msvc
from conan.tools.files import export_conandata_patches, apply_conandata_patches, get, chdir, rmdir, copy, rm
from conan.tools.env import Environment
from conans import MSBuild, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment
from conans.tools import vcvars, environment_append
import os

required_conan_version = ">=1.52.0"


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
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not is_msvc(self):
            if "CONAN_BASH_PATH" not in Environment().vars(self, scope="build").keys():
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _build_msvc(self):
        with chdir(self, self._source_subfolder):
            with vcvars(self), environment_append(VisualStudioBuildEnvironment(self).vars):
                target = "libdeflate.dll" if self.options.shared else "libdeflatestatic.lib"
                self.run("nmake /f Makefile.msc {}".format(target))

    def _build_make(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=(self._settings_build.os == "Windows"))
        with chdir(self, self._source_subfolder):
            autotools.make()

    def build(self):
        apply_conandata_patches(self)
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
        autotools = AutoToolsBuildEnvironment(self, win_bash=(self._settings_build.os == "Windows"))
        with chdir(self, self._source_subfolder):
            autotools.install(args=["PREFIX={}".format(self.package_folder)])
        rmdir(self, os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.a" if self.options.shared else "*.[so|dylib]*", os.path.join(self.package_folder, "lib") )

    def package(self):
        copy(self, "COPYING", 
            src=os.path.join(self.source_folder, self._source_subfolder), 
            dst=os.path.join(self.package_folder, "licenses"
        ))
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
