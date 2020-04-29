from conans import ConanFile, tools
from conans.tools import Version
from conans.errors import ConanInvalidConfiguration
import os

class Stlab(ConanFile):
    name = 'stlab'
    description = 'The Software Technology Lab libraries.'
    url = 'https://github.com/conan-io/conan-center-index'
    homepage = 'https://github.com/stlab/libraries'
    license = 'BSL-1.0'
    topics = 'conan', 'c++', 'concurrency', 'futures', 'channels'

    settings = 'compiler'

    options = {
        'coroutines': [True, False]
    }
    default_options = {
        'coroutines': False
    }

    no_copy_source = True
    _source_subfolder = 'source_subfolder'

    requires = 'boost/1.69.0'

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "libraries-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, '17')

        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "9":
            raise ConanInvalidConfiguration("Need gcc >= 9")

        if self.settings.compiler == "clang" and Version(self.settings.compiler.version) < "8":
            raise ConanInvalidConfiguration("Need clang >= 8")

        if self.settings.compiler == "Visual Studio" and Version(self.settings.compiler.version) < "15.8":
            raise ConanInvalidConfiguration("Need Visual Studio >= 2017 15.8 (MSVC 19.15)")

    def package(self):
        self.copy("*LICENSE", dst="licenses", keep_path=False)
        self.copy("stlab/*", src=self._source_subfolder, dst='include/')

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        coroutines_value = 1 if self.options.coroutines else 0

        self.cpp_info.defines = [
            'STLAB_FUTURE_COROUTINES={}'.format(coroutines_value)
        ]
