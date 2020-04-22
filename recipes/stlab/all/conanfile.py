from conans import ConanFile, tools
import os

class Stlab(ConanFile):
    name = 'stlab'
    description = 'The Software Technology Lab libraries.'
    url = 'https://github.com/conan-io/conan-center-index'
    homepage = 'https://github.com/stlab/libraries'
    license = 'BSL-1.0'
    topics = 'conan', 'c++', 'concurrency', 'futures', 'channels'

    settings = 'compiler'

    no_copy_source = True
    _source_subfolder = 'source_subfolder'

    requires = 'boost/1.69.0'

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "libraries-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def configure(self):
        # TODO: Enable transitive required C++17
        # tools.check_min_cppstd(self, '17')
        pass

    def package(self):
        self.copy("*LICENSE", dst="licenses", keep_path=False)
        self.copy("stlab/*", src=self._source_subfolder, dst='include/')

    def package_id(self):
        self.info.header_only()
