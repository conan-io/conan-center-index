from conans import tools, ConanFile
import os


class GslLiteConan(ConanFile):
    name = "gsl-lite"
    version = "0.34.0"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    generators = "cmake"
    homepage = "https://github.com/martinmoene/gsl-lite"
    topics = ("GSL")
    description = ("A single-file header-only version of ISO C++ ",
                   "Guideline Support Library (GSL) for C++98, C++11 and later")
    _source_subfolder = "source_subfolder"
    no_copy_source = True
    #  There are three configuration options for this GSL implementation's behavior
    #  when pre/post conditions on the GSL types are violated:
    # 
    #  1. GSL_TERMINATE_ON_CONTRACT_VIOLATION: std::terminate will be called (default)
    #  2. GSL_THROW_ON_CONTRACT_VIOLATION: a gsl::fail_fast exception will be thrown
    #  3. GSL_UNENFORCED_ON_CONTRACT_VIOLATION: nothing happens
    # 
    options = {
        'on_contract_violation': ['terminate', 'throw', 'unenforced']
    }

    default_options = {
        'on_contract_violation': 'terminate',
    }

    _contract_map = {
        'terminate': 'GSL_TERMINATE_ON_CONTRACT_VIOLATION',
        'throw': 'GSL_THROW_ON_CONTRACT_VIOLATION',
        'unenforced': 'GSL_UNENFORCED_ON_CONTRACT_VIOLATION'
    }

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("*gsl-lite.hpp", src=self._source_subfolder)
        self.copy("*LICENSE", dst="licenses", keep_path=False)

    def package_info(self):
        self.cpp_info.defines = [self._contract_map[str(self.options.on_contract_violation)]]

    def package_id(self):
        self.info.header_only()
