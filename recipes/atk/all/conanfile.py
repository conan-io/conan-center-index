from conans import ConanFile, Meson, tools
from conans.errors import ConanInvalidConfiguration
import os
import glob

required_conan_version = ">=1.29"

class AtkConan(ConanFile):
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
        "shared": False,
        "fPIC": True,
        }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def build_requirements(self):
        self.build_requires('meson/0.58.1')
        self.build_requires('pkgconf/1.7.4')

    def requirements(self):
        self.requires('glib/2.68.3')

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_meson(self):
        meson = Meson(self)
        defs = {}
        defs['introspection'] = 'false'
        defs['docs'] = 'false'
        args=[]
        args.append('--wrap-mode=nofallback')
        args.append('--localedir=%s' % os.path.join(self.package_folder, 'bin', 'share', 'locale'))
        meson.configure(defs=defs, build_folder=self._build_subfolder, source_folder=self._source_subfolder, pkg_config_paths='.', args=args)
        return meson

    def build(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, 'meson.build'),
            "subdir('tests')",
            "#subdir('tests')")
        meson = self._configure_meson()
        meson.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        meson = self._configure_meson()
        meson.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        if self.settings.compiler == "Visual Studio":
            for pdb in glob.glob(os.path.join(self.package_folder, "bin", "*.pdb")):
                os.unlink(pdb)
            if not self.options.shared:
                os.rename(os.path.join(self.package_folder, 'lib', 'libatk-1.0.a'), os.path.join(self.package_folder, 'lib', 'atk-1.0.lib'))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = ['include/atk-1.0']
