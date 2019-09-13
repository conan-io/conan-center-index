#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools
import os


class GslMicrosoftConan(ConanFile):
    name = "ms-gsl"
    version = "2.0.0"
    description = "Functions and types that are suggested for use by the C++ Core Guideline"
    url = "https://github.com/bincrafters/conan-gsl_microsoft"
    license = "MIT"
    exports = ["LICENSE.md"]
    no_copy_source = True
    _source_subfolder = "source_subfolder"
    
    
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
        self.cpp_info.defines = [self._contract_map[str(self.options.on_contract_violation)]]
