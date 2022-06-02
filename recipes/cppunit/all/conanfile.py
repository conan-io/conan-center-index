import shutil
from conans import AutoToolsBuildEnvironment, ConanFile, tools, MSBuild
import os

required_conan_version = ">=1.40.0"

class CppunitConan(ConanFile):
    name = "cppunit"
    description = "CppUnit is the C++ port of the famous JUnit framework for unit testing. Test output is in XML for automatic testing and GUI based for supervised tests."
    topics = ("conan", "cppunit", "unit-test", "tdd")
    license = " LGPL-2.1-or-later"
    homepage = "https://freedesktop.org/wiki/Software/cppunit/"
    url = "https://github.com/conan-io/conan-center-index"
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        yes_no = lambda v: "yes" if v else "no"
        conf_args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-debug={}".format(yes_no(self.settings.build_type == "Debug")),
            "--enable-doxygen=no",
            "--enable-dot=no",
            "--enable-werror=no",
            "--enable-html-docs=no",
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        if self.settings.compiler == "Visual Studio":
            project = "cppunit_dll.vcxproj" if self.options.shared else "cppunit.vcxproj"
            msvc_arch = {
                'x86': 'x86',
                'x86_64': 'x64',
                'armv7': 'ARM',
                'armv8': 'ARM64'
            }
            msbuild = MSBuild(self)
            msbuild.build(os.path.join(self._source_subfolder, "src", "cppunit", project), use_env=False)
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        if self.settings.compiler == "Visual Studio":
            shutil.copytree(src=os.path.join(self._source_subfolder, "lib"), dst=os.path.join(self.package_folder, "lib"))
            shutil.copytree(src=os.path.join(self._source_subfolder, "include"), dst=os.path.join(self.package_folder, "include"))
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        libsuffix = "d" if self.settings.compiler == "Visual Studio" and self.settings.build_type == "Debug" else ""
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            self.cpp_info.libs = ["cppunit_dll" + libsuffix]
        else:
            self.cpp_info.libs = ["cppunit" + libsuffix]
        if not self.options.shared:
            stdlib = tools.stdcpp_library(self)
            if stdlib:
                self.cpp_info.system_libs.append(stdlib)
            if self.settings.os == "Linux":
                self.cpp_info.system_libs.append("dl")
        if self.options.shared and self.settings.os == "Windows":
            self.cpp_info.defines.append("CPPUNIT_DLL")
        self.cpp_info.filenames["pkg_config"] = "cppunit"
