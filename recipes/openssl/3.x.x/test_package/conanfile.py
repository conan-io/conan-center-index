import os
import re
from io import StringIO

from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
from conan.tools.scm import Version


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    @property
    def _openssl(self):
        return self.dependencies["openssl"]

    def _with_legacy(self):
        return (not self._openssl.options.no_legacy and
            ((not self._openssl.options.no_md4) or
              (not self._openssl.options.no_rmd160)))

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["OPENSSL_WITH_LEGACY"] = self._with_legacy()
        tc.cache_variables["OPENSSL_WITH_MD4"] = not self._openssl.options.no_md4
        tc.cache_variables["OPENSSL_WITH_RIPEMD160"] = not self._openssl.options.no_rmd160
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
        else:
            self.output.info("Skipping executable smoke test: cannot run on this platform")

        if self._is_fips_enabled():
            self._test_fips()
        else:
            self.output.info("FIPS module test skipped: FIPS disabled in tested package")

    def _is_fips_enabled(self):
        return (not self._openssl.options.no_fips) or self._openssl.options.use_validated_fips

    def _fips_module_filename(self):
        suffix = {"Macos": "dylib", "Windows": "dll"}.get(str(self.settings.os), "so")
        return f"fips.{suffix}"

    def _expected_fips_version(self):
        if self._openssl.options.use_validated_fips:
            versions = ['3.0.8', '3.0.9', '3.1.2']
            versions = sorted([Version(v) for v in versions], reverse=True)
            target_version = next((v for v in versions if v <= Version(self._openssl.ref.version)), None)
            return str(target_version) if target_version is not None else None
        return str(self._openssl.ref.version)

    def _openssl_binary(self):
        bin_suffix = ".exe" if str(self.settings.os) == "Windows" else ""
        return os.path.join(self._openssl.package_folder, "bin", f"openssl{bin_suffix}")

    def _fips_module_path(self):
        return os.path.join(self._openssl.package_folder, "lib", "ossl-modules", self._fips_module_filename())

    def _test_fips(self):
        if not can_run(self):
            self.output.info("FIPS module test skipped: cannot run on this platform")
            return

        openssl_bin = self._openssl_binary()
        fips_module = self._fips_module_path()
        fips_cnf = os.path.join(self.build_folder, "fips.cnf")

        if not os.path.isfile(openssl_bin):
            raise ConanInvalidConfiguration(f"OpenSSL executable not found at {openssl_bin}")
        if not os.path.isfile(fips_module):
            raise ConanInvalidConfiguration(f"FIPS module not found at {fips_module}")

        self.output.info("Testing FIPS module (via fipsinstall & fipsinstall -verify)")

        install_cmd = f"\"{openssl_bin}\" fipsinstall -module \"{fips_module}\" -out \"{fips_cnf}\""
        install_stderr = StringIO()
        try:
            self.run(install_cmd, stderr=install_stderr, env="conanrun")
        except ConanException as e:
            stderr_text = install_stderr.getvalue()
            raise ConanException(f"{str(e)}\n{stderr_text}") from e

        install_text = install_stderr.getvalue()
        self.output.info(install_text)
        if not re.search(r"INSTALL PASSED", install_text):
            raise ConanInvalidConfiguration(f"The FIPS Module could not be installed properly:\n{install_text}")

        expected_version = self._expected_fips_version()
        if expected_version and Version(self._openssl.ref.version) >= "3.1.0":
            self.output.info("Checking FIPS version match")
            version_match = re.search(r"version:\s+(\S+)", install_text)
            installed_version = version_match.group(1) if version_match else None
            if installed_version != expected_version:
                raise ConanInvalidConfiguration(
                    f"The FIPS Module version installed ({installed_version}) does not match the desired version ({expected_version})\n{install_text}"
                )

        verify_cmd = f"\"{openssl_bin}\" fipsinstall -module \"{fips_module}\" -in \"{fips_cnf}\" -verify"
        verify_stderr = StringIO()
        try:
            self.run(verify_cmd, stderr=verify_stderr, env="conanrun")
        except ConanException as e:
            stderr_text = verify_stderr.getvalue()
            raise ConanException(f"{str(e)}\n{stderr_text}") from e

        verify_text = verify_stderr.getvalue()
        self.output.info(verify_text)
        if not re.search(r"VERIFY PASSED", verify_text):
            raise ConanInvalidConfiguration(f"The FIPS Module installation did not verify properly:\n{verify_text}")
