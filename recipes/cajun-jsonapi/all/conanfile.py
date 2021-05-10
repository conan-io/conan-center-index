from conans import ConanFile, tools
import os

class CajunJsonApiConan(ConanFile):
    name = 'cajun-jsonapi'
    description = 'CAJUN* is a C++ API for the JSON object interchange format.'
    topics = ("conan", "cajun", "json")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cajun-jsonapi/cajun-jsonapi"
    license = "BSD-3-Clause"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def _extract_license(self):
        file_content = tools.load(os.path.join(self.source_folder, self._source_subfolder, "test.cpp"))
        return file_content[:file_content.find("*/")]

    def package(self):
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), self._extract_license())
        self.copy('LICENSE', dst='licenses', src=self._source_subfolder)
        self.copy('*.h', dst=os.path.join('include', 'json'), src=os.path.join(self._source_subfolder, 'json'))
        self.copy('*.inl', dst=os.path.join('include', 'json'), src=os.path.join(self._source_subfolder, 'json'))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "cajun"))
