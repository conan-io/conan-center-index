import os
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration

class MicrosoftGslConan(ConanFile):
    name = "ms-gsl"
    description = "Functions and types that are suggested for use by the C++ Core Guideline"
    homepage = "https://github.com/microsoft/GSL"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    topics = ("GSL", "guidelines", "core", "span")
    no_copy_source = True
    
    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

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
        extracted_dir = "GSL-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
            
    def package(self):
        include_folder = os.path.join(self._source_subfolder, "include")
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=include_folder)

    def package_id(self):
        self.info.header_only()
        
    def package_info(self):
        if int(self.version.split(".")[0]) > 2:
            if self.options.on_contract_violation != 'terminate':
                raise ConanInvalidConfiguration("Microsoft GSL only supports terminate on contract violation since version 3.0.0")

        self.cpp_info.defines = [self._contract_map[str(self.options.on_contract_violation)]]
        if int(self.version.split(".")[0]) > 2:
            self.cpp_info.names["cmake_find_package"] = "Microsoft.GSL"
            self.cpp_info.names["cmake_find_package_multi"] = "Microsoft.GSL"
