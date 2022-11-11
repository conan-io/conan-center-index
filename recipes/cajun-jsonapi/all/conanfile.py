from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy, load, save
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class CajunJsonApiConan(ConanFile):
    name = "cajun-jsonapi"
    description = "CAJUN* is a C++ API for the JSON object interchange format."
    topics = ("conan", "cajun", "json")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cajun-jsonapi/cajun-jsonapi"
    license = "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def source(self):
        get(
            self,
            **self.conan_data["sources"][self.version],
            destination=self.source_folder,
            strip_root=True
        )

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, 11)

    def _extract_license(self):
        file_content = load(self, os.path.join(self.source_folder, "test.cpp"))
        return (
            file_content[: file_content.find("*/")]
            .split("\n", 2)[-1]
            .rsplit("\n", 1)[0]
        )

    def package(self):
        package_version = Version(self.version)
        if package_version < "2.1.0":
            # No dedicated LICENSE file in older versions, extracting license text from comments
            save(
                self,
                os.path.join(self.package_folder, "licenses", "LICENSE"),
                self._extract_license(),
            )
            # Prior to v2.1.0 there was no "cajun" subfolder in sources but it was present in RPM packages
            # (e.g. https://centos.pkgs.org/7/epel-x86_64/cajun-jsonapi-devel-2.0.3-2.el7.noarch.rpm.html)
            # For ease of migration from RPM dependencies to Conan creating intermediate "cajun" folder
            # so that '#include "cajun/json/..."' statements worked correctly
            copy(
                self,
                "*.h",
                dst=os.path.join(self.package_folder, "include", "cajun", "json"),
                src=os.path.join(self.source_folder, "json"),
            )
            copy(
                self,
                "*.inl",
                dst=os.path.join(self.package_folder, "include", "cajun", "json"),
                src=os.path.join(self.source_folder, "json"),
            )
        else:
            copy(
                self,
                "*.h",
                dst=os.path.join(self.package_folder, "include"),
                src=os.path.join(self.source_folder, "include"),
            )
            copy(
                self,
                "*.inl",
                dst=os.path.join(self.package_folder, "include"),
                src=os.path.join(self.source_folder, "include"),
            )
        copy(
            self,
            "LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )

    def package_id(self):
        self.info.clear()

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "cajun"))
