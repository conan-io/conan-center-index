from conan import ConanFile, tools
import os

class TypeSafe(ConanFile):
    name = 'type_safe'
    description = 'Zero overhead utilities for preventing bugs at compile time'
    url = 'https://github.com/conan-io/conan-center-index'
    homepage = 'https://foonathan.net/type_safe'
    license = 'MIT'
    topics = 'conan', 'c++', 'strong typing', 'vocabulary-types'

    settings = 'compiler'

    no_copy_source = True
    _source_subfolder = 'source_subfolder'

    requires = 'debug_assert/1.3.3'

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
        self.copy("*", src=os.path.join(self._repo_folder, 'include'), dst='include/')

    def package_id(self):
        self.info.header_only()
