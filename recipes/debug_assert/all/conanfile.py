from conans import ConanFile, tools
import os

class DebugAssert(ConanFile):
    name = 'debug_assert'
    description = 'Simple, flexible and modular assertion macro'
    url = 'https://github.com/conan-io/conan-center-index'
    homepage = 'http://foonathan.net/blog/2016/09/16/assertions.html'
    license = 'Zlib'
    topics = 'conan', 'assert', 'debugging', 'utilities'

    settings = 'compiler'

    no_copy_source = True
    _source_subfolder = 'source_subfolder'

    @property
    def _repo_folder(self):
        return os.path.join(self.source_folder, self._source_subfolder)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = self.name +  "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, '11')

    def package(self):
        self.copy("*LICENSE", dst="licenses", keep_path=False)
        self.copy("debug_assert.hpp", src=self._repo_folder, dst='include/')

    def package_id(self):
        self.info.header_only()
