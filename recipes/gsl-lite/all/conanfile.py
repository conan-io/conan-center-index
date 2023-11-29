from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class GslLiteConan(ConanFile):
    name = "gsl-lite"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/martinmoene/gsl-lite"
    topics = ("GSL",)
    description = "A single-file header-only version of ISO C++ " \
                  "Guideline Support Library (GSL) for C++98, C++11 and later"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    #  There are three configuration options for this GSL implementation's behavior
    #  when pre/post conditions on the GSL types are violated:
    #
    #  1. GSL_TERMINATE_ON_CONTRACT_VIOLATION: std::terminate will be called (default)
    #  2. GSL_THROW_ON_CONTRACT_VIOLATION: a gsl::fail_fast exception will be thrown
    #  3. GSL_UNENFORCED_ON_CONTRACT_VIOLATION: nothing happens
    #
    options = {
        "on_contract_violation": ["terminate", "throw", "unenforced"]
    }
    default_options = {
        "on_contract_violation": "terminate",
    }

    no_copy_source = True

    @property
    def _contract_map(self):
        return {
            "terminate": "GSL_TERMINATE_ON_CONTRACT_VIOLATION",
            "throw": "GSL_THROW_ON_CONTRACT_VIOLATION",
            "unenforced": "GSL_UNENFORCED_ON_CONTRACT_VIOLATION"
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "*", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE",  src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "gsl-lite")
        self.cpp_info.set_property("cmake_target_name", "gsl::gsl-lite")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["gsllite"].defines = [self._contract_map[str(self.options.on_contract_violation)]]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "gsl-lite"
        self.cpp_info.filenames["cmake_find_package_multi"] = "gsl-lite"
        self.cpp_info.names["cmake_find_package"] = "gsl"
        self.cpp_info.names["cmake_find_package_multi"] = "gsl"
        self.cpp_info.components["gsllite"].names["cmake_find_package"] = "gsl-lite"
        self.cpp_info.components["gsllite"].names["cmake_find_package_multi"] = "gsl-lite"
        self.cpp_info.components["gsllite"].set_property("cmake_target_name", "gsl::gsl-lite")
        self.cpp_info.components["gsllite"].bindirs = []
        self.cpp_info.components["gsllite"].libdirs = []
