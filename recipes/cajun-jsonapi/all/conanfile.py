from conan import ConanFile, tools
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
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, 11)

    def _extract_license(self):
        file_content = tools.files.load(self, os.path.join(self.source_folder, self._source_subfolder, "test.cpp"))
        return file_content[:file_content.find("*/")]

    def package(self):
        package_version = tools.scm.Version(self.version)
        if package_version < "2.1.0":
            # No dedicated LICENSE file in older versions, extracting license text from comments
            tools.files.save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._extract_license())
            # Prior to v2.1.0 there was no "cajun" subfolder in sources but it was present in RPM packages
            # (e.g. https://centos.pkgs.org/7/epel-x86_64/cajun-jsonapi-devel-2.0.3-2.el7.noarch.rpm.html)
            # For ease of migration from RPM dependencies to Conan creating intermediate "cajun" folder
            # so that '#include "cajun/json/..."' statements worked correctly
            self.copy('*.h', dst=os.path.join('include', 'cajun', 'json'), src=os.path.join(self._source_subfolder, 'json'))
            self.copy('*.inl', dst=os.path.join('include', 'cajun', 'json'), src=os.path.join(self._source_subfolder, 'json'))
        else:
            self.copy('*.h', dst=os.path.join('include'), src=os.path.join(self._source_subfolder, 'include'))
            self.copy('*.inl', dst=os.path.join('include'), src=os.path.join(self._source_subfolder, 'include'))
        self.copy('LICENSE', dst='licenses', src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "cajun"))
