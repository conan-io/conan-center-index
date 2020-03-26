import os
from conans import ConanFile, tools


class GslMicrosoftConan(ConanFile):
    name = "ms-gsl"
    version = "2.1.0"
    description = "Microsoft implementation of the Guidelines Support Library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/microsoft/GSL"
    topics = ("gsl")
    license = "MIT"
    no_copy_source = True
    _source_subfolder = "source_subfolder"

    #  There are three configuration options for this GSL implementation's behavior
    #  when pre/post conditions on the GSL types are violated:
    #
    #  1. GSL_TERMINATE_ON_CONTRACT_VIOLATION: std::terminate will be called (default)
    #  2. GSL_THROW_ON_CONTRACT_VIOLATION: a gsl::fail_fast exception will be thrown
    #  3. GSL_UNENFORCED_ON_CONTRACT_VIOLATION: nothing happens
    #
    # Warning: This behavior **may** change in the future according to
    # https://github.com/microsoft/GSL/releases/tag/v2.1.0 which states that
    # "Contract violation will always result in termination."
    options = {
        "on_contract_violation": ["terminate", "throw", "unenforced"]
    }

    default_options = {
        "on_contract_violation": "terminate",
    }

    _contract_map = {
        "terminate": "GSL_TERMINATE_ON_CONTRACT_VIOLATION",
        "throw": "GSL_THROW_ON_CONTRACT_VIOLATION",
        "unenforced": "GSL_UNENFORCED_ON_CONTRACT_VIOLATION",
    }

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "GSL-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        # No build step for this header-only library
        pass

    def package(self):
        include_folder = os.path.join(self._source_subfolder, "include")
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=include_folder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.defines = [
            self._contract_map[str(self.options.on_contract_violation)]
        ]
