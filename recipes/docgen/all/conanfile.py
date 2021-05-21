import os
import shutil

from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class DocgenConan(ConanFile):
    name = 'docgen'
    license = 'MIT'
    homepage = 'https://github.com/DavidZemon/docgen.git'
    url = 'https://github.com/conan-io/conan-center-index'
    description = 'Doxygen documentation generation utilities'
    settings = {
        'os': None,
        'compiler': None
    }
    topics = ('doxygen',)

    # Doxygen requires GCC 5 or newer and Doxygen is required by the test_package folder, so do not attempt to provide
    # a package if the compiler version is older than GCC 5
    _minimum_compiler_version = {
        "gcc": 5,
    }

    def configure(self):
        minimum_compiler_version = self._minimum_compiler_version.get(str(self.settings.compiler))
        if minimum_compiler_version is not None:
            if tools.Version(self.settings.compiler.version) < minimum_compiler_version:
                raise ConanInvalidConfiguration("Compiler version too old. At least {} is required.".format(minimum_compiler_version))

    @property
    def _source_subfolder(self):
        return f'{self.name}-{self.version}'

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

    def package(self):
        os.makedirs(os.path.join(f'{self.package_folder}', 'licenses'))
        shutil.copy2(
            os.path.join(self._source_subfolder, 'license.txt'),
            os.path.join(f'{self.package_folder}', 'licenses', self.name)
        )

        os.makedirs(f'{self.package_folder}/res')
        self.copy(
            'resources/*',
            f'{self.package_folder}/res/resources',
            src=self._source_subfolder,
            keep_path=False
        )
        self.copy(
            'Doxyfile.in',
            f'{self.package_folder}/res',
            src=self._source_subfolder,
            keep_path=False
        )
        self.copy(
            'DocGen-functions.cmake',
            f'{self.package_folder}/res',
            src=self._source_subfolder,
            keep_path=False
        )

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.builddirs = [os.path.join('res')]

        self.cpp_info.filenames['cmake_find_package'] = 'DocGen'
        self.cpp_info.filenames['cmake_find_package_multi'] = 'DocGen'
        self.cpp_info.build_modules = [os.path.join('res', 'DocGen-functions.cmake')]
