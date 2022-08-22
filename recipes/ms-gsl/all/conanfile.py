import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.50.0"


class MicrosoftGslConan(ConanFile):
    name = "ms-gsl"
    description = "Microsoft implementation of the Guidelines Support Library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/microsoft/GSL"
    license = "MIT"
    topics = ("gsl", "guidelines", "core", "span")
    no_copy_source = True
    settings = "compiler"
    options = {
        "on_contract_violation": ["terminate", "throw", "unenforced"]
    }
    default_options = {
        "on_contract_violation": "terminate"
    }

    @property
    def _contract_map(self):
        return {
            "terminate": "GSL_TERMINATE_ON_CONTRACT_VIOLATION",
            "throw": "GSL_THROW_ON_CONTRACT_VIOLATION",
            "unenforced": "GSL_UNENFORCED_ON_CONTRACT_VIOLATION",
        }

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "clang": "3.4",
            "apple-clang": "3.4",
        }

    def validate(self):
        check_min_cppstd(self, 14)
        check_min_vs(self, "190")

        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version:
                if Version(self.settings.compiler.version) < minimum_version:
                    raise ConanInvalidConfiguration("ms-gsl requires C++14, which your compiler does not fully support.")
            else:
                self.output.warn("ms-gsl requires C++14. Your compiler is unknown. Assuming it supports C++14.")

    def config_options(self):
        if Version(self.version) >= "3.0.0":
            del self.options.on_contract_violation

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Microsoft.GSL")
        self.cpp_info.set_property("cmake_target_name", "Microsoft.GSL::GSL")

        self.cpp_info.filenames["cmake_find_package"] = "Microsoft.GSL"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Microsoft.GSL"
        self.cpp_info.names["cmake_find_package"] = "Microsoft.GSL"
        self.cpp_info.names["cmake_find_package_multi"] = "Microsoft.GSL"

        self.cpp_info.components["_ms-gsl"].names["cmake_find_package"] = "GSL"
        self.cpp_info.components["_ms-gsl"].names["cmake_find_package_multi"] = "GSL"

        if Version(self.version) < "3.0.0":
            self.cpp_info.components["_ms-gsl"].defines = [
                self._contract_map[str(self.options.on_contract_violation)]
            ]
