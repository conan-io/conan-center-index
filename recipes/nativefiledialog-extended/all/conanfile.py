from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rmdir, rm
import os

required_conan_version = '>=1.53.0'

class NativeFileDialogExtendedConan(ConanFile):
    name = 'nativefiledialog-extended'
    license = 'Zlib'
    url = 'https://github.com/conan-io/conan-center-index'
    homepage = 'https://github.com/btzy/nativefiledialog-extended'
    description = 'A tiny, neat C library that portably invokes native file open and save dialogs. Includes basic C++ wrapper'
    topics = ('dialog', 'gui', 'filedialog')
    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {
        'shared': [True, False],
        'fPIC': [True, False],
        'auto_extension': [True, False],
        'use_portal': [True, False],
        'force_allowedFileTypes': [True, False],
    }
    default_options = {
        'shared': False,
        'fPIC': True,
        'auto_extension': False,
        'use_portal': False,
        'force_allowedFileTypes': False,
    }

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        if self.settings.os == 'Linux':
            if self.options.use_portal:
                self.requires('dbus/1.15.2')
            else:
                self.requires('gtk/3.24.24')

    def configure(self):
        if self.settings.os == 'Windows':
            self.options.rm_safe('fPIC')
            self.options.rm_safe('auto_extension')
            self.options.rm_safe('use_portal')
            self.options.rm_safe('force_allowedFileTypes')
        if self.settings.os == 'Linux':
            self.options.rm_safe('force_allowedFileTypes')
        if self.settings.os == 'Macos':
            self.options.rm_safe('auto_extension')
            self.options.rm_safe('use_portal')

    def source(self):
        get(self, **self.conan_data['sources'][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables['NFD_BUILD_TESTS'] = False
        tc.variables['NFD_INSTALL'] = True
        if self.settings.os == 'Macos':
            tc.variables['NFD_USE_ALLOWEDCONTENTTYPES_IF_AVAILABLE'] = not self.options.force_allowedFileTypes
        elif self.settings.os == 'Linux':
            tc.variables['NFD_PORTAL'] = self.options.use_portal
            tc.variables['NFD_APPEND_EXTENSION'] = self.options.auto_extension
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, 'lib', 'cmake'))
        rmdir(self, os.path.join(self.package_folder, 'lib', 'pkgconfig'))
        rm(self, '*.la', os.path.join(self.package_folder, 'lib'))
        rm(self, '*.pdb', os.path.join(self.package_folder, 'lib'))
        rm(self, '*.pdb', os.path.join(self.package_folder, 'bin'))

        copy(self, pattern='LICENSE', dst=os.path.join(self.package_folder, 'licenses'), src=self.source_folder)

    def package_info(self):
        self.cpp_info.libs = ['nfd']
        if self.settings.os == 'Macos':
            self.cpp_info.frameworks = ['AppKit', 'UniformTypeIdentifiers']
        elif self.settings.os == 'Windows':
            self.cpp_info.system_libs = ['shell32.lib', 'ole32.lib', 'uuid.lib']
