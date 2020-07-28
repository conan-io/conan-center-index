from conans import ConanFile, Meson, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil


class LibnameConan(ConanFile):
    name = "atk"
    description = "set of accessibility interfaces that are implemented by other toolkits and applications"
    topics = ("conan", "atk", "accessibility")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.atk.org"
    license = "LGPL-2.1-or-later"
    generators = "pkg_config"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        }
    default_options = {
        "shared": True,
        "fPIC": True,
        }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
    
    def build_requirements(self):
        self.build_requires('meson/0.55.0')
        if not tools.which('pkg-config') or self.settings.os == "Windows":
            self.build_requires('pkgconf/1.7.3')
    
    def requirements(self):
        self.requires('glib/2.65.0')

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        tools.replace_in_file(os.path.join(self._source_subfolder, 'meson.build'),
            "subdir('tests')",
            "#subdir('tests')")

    def _configure_meson(self):
        meson = Meson(self)
        defs = {}
        defs['introspection'] = 'false'
        defs['docs'] = 'false'
        args=[]
        args.append('--wrap-mode=nofallback')
        meson.configure(defs=defs, build_folder=self._build_subfolder, source_folder=self._source_subfolder, pkg_config_paths='.', args=args)
        return meson

    def build(self):
        for package in self.deps_cpp_info.deps:
            lib_path = self.deps_cpp_info[package].rootpath
            for dirpath, _, filenames in os.walk(lib_path):
                for filename in filenames:
                    if filename.endswith('.pc'):
                        shutil.copyfile(os.path.join(dirpath, filename), filename)
                        tools.replace_prefix_in_pc_file(filename, lib_path)
        meson = self._configure_meson()
        meson.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        meson = self._configure_meson()
        meson.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        if self.settings.compiler == "Visual Studio" and not self.options.shared:
            os.rename(os.path.join(self.package_folder, 'lib', 'libatk-1.0.a'), os.path.join(self.package_folder, 'lib', 'atk-1.0.lib'))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = ['include/atk-1.0']
