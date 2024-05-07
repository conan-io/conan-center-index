import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
    replace_in_file,
)

required_conan_version = ">=1.60.0"


port_include_directories = {
    "BCC_16BIT_DOS_FLSH186": [
        os.path.join("BCC", "16BitDOS", "common"),
        os.path.join("BCC", "16BitDOS", "Flsh186"),
    ],
    "BCC_16BIT_DOS_PC": [
        os.path.join("BCC", "16BitDOS", "common"),
        os.path.join("BCC", "16BitDOS", "PC"),
    ],
    "CCS_ARM_CM3": [os.path.join("CCS", "ARM_CM3")],
    "CCS_ARM_CM4F": [os.path.join("CCS", "ARM_CM4F")],
    "CCS_ARM_CR4": [os.path.join("CCS", "ARM_Cortex-R4")],
    "CCS_MSP430X": [os.path.join("CCS", "MSP430X")],
    "CODEWARRIOR_COLDFIRE_V1": [os.path.join("CodeWarrior", "ColdFire_V1")],
    "CODEWARRIOR_COLDFIRE_V2": [os.path.join("CodeWarrior", "ColdFire_V2")],
    "CODEWARRIOR_HCS12": [os.path.join("CodeWarrior", "HCS12")],
    "GCC_ARM_CA9": [os.path.join("GCC", "ARM_CA9")],
    "GCC_Arm_AARCH64": [os.path.join("GCC", "Arm_AARCH64")],
    "GCC_Arm_AARCH64_SRE": [os.path.join("GCC", "Arm_AARCH64_SRE")],
    "GCC_ARM_CM0": [os.path.join("GCC", "ARM_CM0")],
    "GCC_ARM_CM3": [os.path.join("GCC", "ARM_CM3")],
    "GCC_ARM_CM3_MPU": [os.path.join("GCC", "ARM_CM3_MPU")],
    "GCC_ARM_CM4_MPU": [os.path.join("GCC", "ARM_CM4_MPU")],
    "GCC_ARM_CM4F": [os.path.join("GCC", "ARM_CM4F")],
    "GCC_ARM_CM7": [os.path.join("GCC", "ARM_CM7", "r0p1")],
    "GCC_ARM_CM23_NONSECURE": [os.path.join("GCC", "ARM_CM23", "non_secure")],
    "GCC_ARM_CM23_SECURE": [os.path.join("GCC", "ARM_CM23", "secure")],
    "GCC_ARM_CM23_NTZ_NONSECURE": [os.path.join("GCC", "ARM_CM23_NTZ", "non_secure")],
    "GCC_ARM_CM33_NONSECURE": [os.path.join("GCC", "ARM_CM33", "non_secure")],
    "GCC_ARM_CM33_SECURE": [os.path.join("GCC", "ARM_CM33", "secure")],
    "GCC_ARM_CM33_NTZ_NONSECURE": [os.path.join("GCC", "ARM_CM33_NTZ", "non_secure")],
    "GCC_ARM_CM33_TFM": [os.path.join("GCC", "ARM_CM33_NTZ", "non_secure")],
    "GCC_ARM_CM35P_NONSECURE": [os.path.join("GCC", "ARM_CM35P", "non_secure")],
    "GCC_ARM_CM35P_SECURE": [os.path.join("GCC", "ARM_CM35P", "secure")],
    "GCC_ARM_CM35P_NTZ_NONSECURE": [os.path.join("GCC", "ARM_CM35P_NTZ", "non_secure")],
    "GCC_ARM_CM55_NONSECURE": [os.path.join("GCC", "ARM_CM55", "non_secure")],
    "GCC_ARM_CM55_SECURE": [os.path.join("GCC", "ARM_CM55", "secure")],
    "GCC_ARM_CM55_NTZ_NONSECURE": [os.path.join("GCC", "ARM_CM55_NTZ", "non_secure")],
    "GCC_ARM_CM55_TFM": [os.path.join("GCC", "ARM_CM55_NTZ", "non_secure")],
    "GCC_ARM_CM85_NONSECURE": [os.path.join("GCC", "ARM_CM85", "non_secure")],
    "GCC_ARM_CM85_SECURE": [os.path.join("GCC", "ARM_CM85", "secure")],
    "GCC_ARM_CM85_NTZ_NONSECURE": [os.path.join("GCC", "ARM_CM85_NTZ", "non_secure")],
    "GCC_ARM_CM85_TFM": [os.path.join("GCC", "ARM_CM85_NTZ", "non_secure")],
    "GCC_ARM_CR5": [os.path.join("GCC", "ARM_CR5")],
    "GCC_ARM_CRX_MPU": [os.path.join("GCC", "ARM_CRx_MPU")],
    "GCC_ARM_CRX_NOGIC": [os.path.join("GCC", "ARM_CRx_No_GIC")],
    "GCC_ARM7_AT91FR40008": [os.path.join("GCC", "ARM7_AT91FR40008")],
    "GCC_ARM7_AT91SAM7S": [os.path.join("GCC", "ARM7_AT91SAM7S")],
    "GCC_ARM7_LPC2000": [os.path.join("GCC", "ARM7_LPC2000")],
    "GCC_ARM7_LPC23XX": [os.path.join("GCC", "ARM7_LPC23xx")],
    "GCC_ATMEGA323": [os.path.join("GCC", "ATMega323")],
    "GCC_AVR32_UC3": [os.path.join("GCC", "AVR32_UC3")],
    "GCC_COLDFIRE_V2": [os.path.join("GCC", "ColdFire_V2")],
    "GCC_CORTUS_APS3": [os.path.join("GCC", "CORTUS_APS3")],
    "GCC_H8S2329": [os.path.join("GCC", "H8S2329")],
    "GCC_HCS12": [os.path.join("GCC", "HCS12")],
    "GCC_IA32_FLAT": [os.path.join("GCC", "IA32_flat")],
    "GCC_MICROBLAZE": [os.path.join("GCC", "MicroBlaze")],
    "GCC_MICROBLAZE_V8": [os.path.join("GCC", "MicroBlazeV8")],
    "GCC_MICROBLAZE_V9": [os.path.join("GCC", "MicroBlazeV9")],
    "GCC_MSP430F449": [os.path.join("GCC", "MSP430F449")],
    "GCC_NIOSII": [os.path.join("GCC", "NiosII")],
    "GCC_PPC405_XILINX": [os.path.join("GCC", "PPC405_Xilinx")],
    "GCC_PPC440_XILINX": [os.path.join("GCC", "PPC440_Xilinx")],
    "GCC_RISC_V": [
        os.path.join("GCC", "RISC-V"),
        os.path.join(
            "GCC",
            "RISC-V",
            "chip_specific_extensions",
            "RISCV_MTIME_CLINT_no_extensions",
        ),
    ],
    "GCC_RISC_V_PULPINO_VEGA_RV32M1RM": [
        os.path.join("GCC", "RISC-V"),
        os.path.join(
            "GCC", "RISC-V", "chip_specific_extensions", "Pulpino_Vega_RV32M1RM"
        ),
    ],
    "GCC_RISC_V_GENERIC": [
        os.path.join("GCC", "RISC-V"),
    ],
    "GCC_RL78": [os.path.join("GCC", "RL78")],
    "GCC_RX100": [os.path.join("GCC", "RX100")],
    "GCC_RX200": [os.path.join("GCC", "RX200")],
    "GCC_RX600": [os.path.join("GCC", "RX600")],
    "GCC_RX600_V2": [os.path.join("GCC", "RX600v2")],
    "GCC_RX700_V3_DPFPU": [os.path.join("GCC", "RX700v3_DPFPU")],
    "GCC_STR75X": [os.path.join("GCC", "STR75x")],
    "GCC_TRICORE_1782": [os.path.join("GCC", "TriCore_1782STR75x")],
    "GCC_ARC_EM_HS": [os.path.join("ThirdParty", "GCC", "ARC_EM_HS")],
    "GCC_ARC_V1": [os.path.join("ThirdParty", "GCC", "ARC_v1")],
    "GCC_ATMEGA": [os.path.join("ThirdParty", "GCC", "ATmega")],
    "GCC_POSIX": [
        os.path.join("ThirdParty", "GCC", "Posix"),
        os.path.join("ThirdParty", "GCC", "Posix", "utils"),
    ],
    "GCC_RP2040": [os.path.join("ThirdParty", "GCC", "RP2040", "include")],
    "GCC_XTENSA_ESP32": [
        os.path.join("ThirdParty", "GCC", "Xtensa_ESP32"),
        os.path.join("ThirdParty", "GCC", "Xtensa_ESP32", "include"),
    ],
    "GCC_AVRDX": [
        os.path.join("ThirdParty", "Partner-Supported-Ports", "GCC", "AVR_AVRDx")
    ],
    "GCC_AVR_MEGA0": [
        os.path.join("ThirdParty", "Partner-Supported-Ports", "GCC", "AVR_Mega0")
    ],
    "IAR_78K0K": [os.path.join("IAR", "78K0R")],
    "IAR_ARM_CA5_NOGIC": [os.path.join("IAR", "ARM_CA5_No_GIC")],
    "IAR_ARM_CA9": [os.path.join("IAR", "ARM_CA9")],
    "IAR_ARM_CM0": [os.path.join("IAR", "ARM_CM0")],
    "IAR_ARM_CM3": [os.path.join("IAR", "ARM_CM3")],
    "IAR_ARM_CM4F": [os.path.join("IAR", "ARM_CM4F")],
    "IAR_ARM_CM4F_MPU": [os.path.join("IAR", "ARM_CM4F_MPU")],
    "IAR_ARM_CM7": [os.path.join("IAR", "ARM_CM7", "r0p1")],
    "IAR_ARM_CM23_NONSECURE": [os.path.join("IAR", "ARM_CM23", "non_secure")],
    "IAR_ARM_CM23_SECURE": [os.path.join("IAR", "ARM_CM23", "secure")],
    "IAR_ARM_CM23_NTZ_NONSECURE": [os.path.join("IAR", "ARM_CM23_NTZ", "non_secure")],
    "IAR_ARM_CM33_NONSECURE": [os.path.join("IAR", "ARM_CM33", "non_secure")],
    "IAR_ARM_CM33_SECURE": [os.path.join("IAR", "ARM_CM33", "secure")],
    "IAR_ARM_CM33_NTZ_NONSECURE": [os.path.join("IAR", "ARM_CM33_NTZ", "non_secure")],
    "IAR_ARM_CM35P_NONSECURE": [os.path.join("IAR", "ARM_CM35P", "non_secure")],
    "IAR_ARM_CM35P_SECURE": [os.path.join("IAR", "ARM_CM35P", "secure")],
    "IAR_ARM_CM35P_NTZ_NONSECURE": [os.path.join("IAR", "ARM_CM35P_NTZ", "non_secure")],
    "IAR_ARM_CM55_NONSECURE": [os.path.join("IAR", "ARM_CM55", "non_secure")],
    "IAR_ARM_CM55_SECURE": [os.path.join("IAR", "ARM_CM55", "secure")],
    "IAR_ARM_CM55_NTZ_NONSECURE": [os.path.join("IAR", "ARM_CM55_NTZ", "non_secure")],
    "IAR_ARM_CM85_NONSECURE": [os.path.join("IAR", "ARM_CM85", "non_secure")],
    "IAR_ARM_CM85_SECURE": [os.path.join("IAR", "ARM_CM85", "secure")],
    "IAR_ARM_CM85_NTZ_NONSECURE": [os.path.join("IAR", "ARM_CM85_NTZ", "non_secure")],
    "IAR_ARM_CRX_NOGIC": [os.path.join("IAR", "ARM_CRx_No_GIC")],
    "IAR_ATMEGA323": [os.path.join("IAR", "ATMega323")],
    "IAR_ATMEL_SAM7S64": [os.path.join("IAR", "AtmelSAM7S64")],
    "IAR_ATMEL_SAM9XE": [os.path.join("IAR", "AtmelSAM9XE")],
    "IAR_AVR_AVRDX": [os.path.join("IAR", "AVR_AVRDx")],
    "IAR_AVR_MEGA0": [os.path.join("IAR", "AVR_Mega0")],
    "IAR_AVR32_UC3": [os.path.join("IAR", "AVR32_UC3")],
    "IAR_LPC2000": [os.path.join("IAR", "LPC2000")],
    "IAR_MSP430": [os.path.join("IAR", "MSP430")],
    "IAR_MSP430X": [os.path.join("IAR", "MSP430X")],
    "IAR_RISC_V": [
        os.path.join("IAR", "RISC-V"),
        os.path.join(
            "IAR", "RISC-V", "chip_specific_extensions", "RV32I_CLINT_no_extensions"
        ),
    ],
    "IAR_RISC_V_GENERIC": [
        os.path.join("IAR", "RISC-V"),
    ],
    "IAR_RL78": [os.path.join("IAR", "RL78")],
    "IAR_RX100": [os.path.join("IAR", "RX100")],
    "IAR_RX600": [os.path.join("IAR", "RX600")],
    "IAR_RX700_V3_DPFPU": [os.path.join("IAR", "RX700v3_DPFPU")],
    "IAR_RX_V2": [os.path.join("IAR", "RXv2")],
    "IAR_STR71X": [os.path.join("IAR", "STR71x")],
    "IAR_STR75X": [os.path.join("IAR", "STR75x")],
    "IAR_STR91X": [os.path.join("IAR", "STR91x")],
    "IAR_V850ES_FX3": [os.path.join("IAR", "V850ES")],
    "IAR_V850ES_HX3": [os.path.join("IAR", "V850ES")],
    "MIKROC_ARM_CM4F": [os.path.join("MikroC", "ARM_CM4F")],
    "MPLAB_PIC18F": [os.path.join("MPLAB", "PIC18F")],
    "MPLAB_PIC24": [os.path.join("MPLAB", "PIC24_dsPIC")],
    "MPLAB_PIC32MEC14XX": [os.path.join("MPLAB", "PIC32MEC14xx")],
    "MPLAB_PIC32MX": [os.path.join("MPLAB", "PIC32MX")],
    "MPLAB_PIC32MZ": [os.path.join("MPLAB", "PIC32MZ")],
    "MSVC_MINGW": ["MSVC-MingW"],
    "OWATCOM_16BIT_DOS_FLSH186": [
        os.path.join("oWatcom", "16BitDOS", "common"),
        os.path.join("oWatcom", "16BitDOS", "Flsh186"),
    ],
    "OWATCOM_16BIT_DOS_PC": [
        os.path.join("oWatcom", "16BitDOS", "common"),
        os.path.join("oWatcom", "16BitDOS", "PC"),
    ],
    "PARADIGM_TERN_EE_LARGE": [os.path.join("Paradigm", "Tern_EE", "large_untested")],
    "PARADIGM_TERN_EE_SMALL": [os.path.join("Paradigm", "Tern_EE", "small")],
    "RENESAS_RX100": [os.path.join("Renesas", "RX100")],
    "RENESAS_RX200": [os.path.join("Renesas", "RX200")],
    "RENESAS_RX600": [os.path.join("Renesas", "RX600")],
    "RENESAS_RX600_V2": [os.path.join("Renesas", "RX600v2")],
    "RENESAS_RX700_V3_DPFPU": [os.path.join("Renesas", "RX700v3_DPFPU")],
    "RENESAS_SH2A_FPU": [os.path.join("Renesas", "SH2A_FPU")],
    "ROWLEY_MSP430F449": [os.path.join("Rowley", "MSP430F449")],
    "RVDS_ARM_CA9": [os.path.join("RVDS", "ARM_CA9")],
    "RVDS_ARM_CM0": [os.path.join("RVDS", "ARM_CM0")],
    "RVDS_ARM_CM3": [os.path.join("RVDS", "ARM_CM3")],
    "RVDS_ARM_CM4_MPU": [os.path.join("RVDS", "ARM_CM4_MPU")],
    "RVDS_ARM_CM4F": [os.path.join("RVDS", "ARM_CM4F")],
    "RVDS_ARM_CM7": [os.path.join("RVDS", "ARM_CM7", "r0p1")],
    "RVDS_ARM7_LPC21XX": [os.path.join("RVDS", "ARM7_LPC21xx")],
    "SDCC_CYGNAL": [os.path.join("SDCC", "Cygnal")],
    "SOFTUNE_MB91460": [os.path.join("Softune", "MB91460")],
    "SOFTUNE_MB96340": [os.path.join("Softune", "MB96340")],
    "TASKING_ARM_CM4F": [os.path.join("Tasking", "ARM_CM4F")],
    "TEMPLATE": ["template"],
    "CDK_THEAD_CK802": [os.path.join("ThirdParty", "CDK", "T-HEAD_CK802")],
    "XCC_XTENSA": [os.path.join("ThirdParty", "XCC", "Xtensa")],
    "WIZC_PIC18": [os.path.join("WizC", "PIC18")],
}


class FreeRTOSKernelConan(ConanFile):
    name = "freertos-kernel"
    description = "The FreeRTOS Kernel library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.freertos.org/"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    topics = ("freertos", "realtime", "rtos")
    package_type = "library"
    short_paths = True
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        "port": [
            "A_CUSTOM_PORT",
            "BCC_16BIT_DOS_FLSH186",
            "BCC_16BIT_DOS_PC",
            "CCS_ARM_CM3",
            "CCS_ARM_CM4F",
            "CCS_ARM_CR4",
            "CCS_MSP430X",
            "CODEWARRIOR_COLDFIRE_V1",
            "CODEWARRIOR_COLDFIRE_V2",
            "CODEWARRIOR_HCS12",
            "GCC_ARM_CA9",
            "GCC_Arm_AARCH64",
            "GCC_Arm_AARCH64_SRE",
            "GCC_ARM_CM0",
            "GCC_ARM_CM3",
            "GCC_ARM_CM3_MPU",
            "GCC_ARM_CM4_MPU",
            "GCC_ARM_CM4F",
            "GCC_ARM_CM7",
            "GCC_ARM_CM23_NONSECURE",
            "GCC_ARM_CM23_SECURE",
            "GCC_ARM_CM23_NTZ_NONSECURE",
            "GCC_ARM_CM33_NONSECURE",
            "GCC_ARM_CM33_SECURE",
            "GCC_ARM_CM33_NTZ_NONSECURE",
            "GCC_ARM_CM33_TFM",
            "GCC_ARM_CM35P_NONSECURE",
            "GCC_ARM_CM35P_SECURE",
            "GCC_ARM_CM35P_NTZ_NONSECURE",
            "GCC_ARM_CM55_NONSECURE",
            "GCC_ARM_CM55_SECURE",
            "GCC_ARM_CM55_NTZ_NONSECURE",
            "GCC_ARM_CM55_TFM",
            "GCC_ARM_CM85_NONSECURE",
            "GCC_ARM_CM85_SECURE",
            "GCC_ARM_CM85_NTZ_NONSECURE",
            "GCC_ARM_CM85_TFM",
            "GCC_ARM_CR5",
            "GCC_ARM_CRX_MPU",
            "GCC_ARM_CRX_NOGIC",
            "GCC_ARM7_AT91FR40008",
            "GCC_ARM7_AT91SAM7S",
            "GCC_ARM7_LPC2000",
            "GCC_ARM7_LPC23XX",
            "GCC_ATMEGA323",
            "GCC_AVR32_UC3",
            "GCC_COLDFIRE_V2",
            "GCC_CORTUS_APS3",
            "GCC_H8S2329",
            "GCC_HCS12",
            "GCC_IA32_FLAT",
            "GCC_MICROBLAZE",
            "GCC_MICROBLAZE_V8",
            "GCC_MICROBLAZE_V9",
            "GCC_MSP430F449",
            "GCC_NIOSII",
            "GCC_PPC405_XILINX",
            "GCC_PPC440_XILINX",
            "GCC_RISC_V",
            "GCC_RISC_V_PULPINO_VEGA_RV32M1RM",
            "GCC_RISC_V_GENERIC",
            "GCC_RL78",
            "GCC_RX100",
            "GCC_RX200",
            "GCC_RX600",
            "GCC_RX600_V2",
            "GCC_RX700_V3_DPFPU",
            "GCC_STR75X",
            "GCC_TRICORE_1782",
            "GCC_ARC_EM_HS",
            "GCC_ARC_V1",
            "GCC_ATMEGA",
            "GCC_POSIX",
            "GCC_RP2040",
            "GCC_XTENSA_ESP32",
            "GCC_AVRDX",
            "GCC_AVR_MEGA0",
            "IAR_78K0K",
            "IAR_ARM_CA5_NOGIC",
            "IAR_ARM_CA9",
            "IAR_ARM_CM0",
            "IAR_ARM_CM3",
            "IAR_ARM_CM4F",
            "IAR_ARM_CM4F_MPU",
            "IAR_ARM_CM7",
            "IAR_ARM_CM23_NONSECURE",
            "IAR_ARM_CM23_SECURE",
            "IAR_ARM_CM23_NTZ_NONSECURE",
            "IAR_ARM_CM33_NONSECURE",
            "IAR_ARM_CM33_SECURE",
            "IAR_ARM_CM33_NTZ_NONSECURE",
            "IAR_ARM_CM35P_NONSECURE",
            "IAR_ARM_CM35P_SECURE",
            "IAR_ARM_CM35P_NTZ_NONSECURE",
            "IAR_ARM_CM55_NONSECURE",
            "IAR_ARM_CM55_SECURE",
            "IAR_ARM_CM55_NTZ_NONSECURE",
            "IAR_ARM_CM85_NONSECURE",
            "IAR_ARM_CM85_SECURE",
            "IAR_ARM_CM85_NTZ_NONSECURE",
            "IAR_ARM_CRX_NOGIC",
            "IAR_ATMEGA323",
            "IAR_ATMEL_SAM7S64",
            "IAR_ATMEL_SAM9XE",
            "IAR_AVR_AVRDX",
            "IAR_AVR_MEGA0",
            "IAR_AVR32_UC3",
            "IAR_LPC2000",
            "IAR_MSP430",
            "IAR_MSP430X",
            "IAR_RISC_V",
            "IAR_RISC_V_GENERIC",
            "IAR_RL78",
            "IAR_RX100",
            "IAR_RX600",
            "IAR_RX700_V3_DPFPU",
            "IAR_RX_V2",
            "IAR_STR71X",
            "IAR_STR75X",
            "IAR_STR91X",
            "IAR_V850ES_FX3",
            "IAR_V850ES_HX3",
            "MIKROC_ARM_CM4F",
            "MPLAB_PIC18F",
            "MPLAB_PIC24",
            "MPLAB_PIC32MEC14XX",
            "MPLAB_PIC32MX",
            "MPLAB_PIC32MZ",
            "MSVC_MINGW",
            "OWATCOM_16BIT_DOS_FLSH186",
            "OWATCOM_16BIT_DOS_PC",
            "PARADIGM_TERN_EE_LARGE",
            "PARADIGM_TERN_EE_SMALL",
            "RENESAS_RX100",
            "RENESAS_RX200",
            "RENESAS_RX600",
            "RENESAS_RX600_V2",
            "RENESAS_RX700_V3_DPFPU",
            "RENESAS_SH2A_FPU",
            "ROWLEY_MSP430F449",
            "RVDS_ARM_CA9",
            "RVDS_ARM_CM0",
            "RVDS_ARM_CM3",
            "RVDS_ARM_CM4_MPU",
            "RVDS_ARM_CM4F",
            "RVDS_ARM_CM7",
            "RVDS_ARM7_LPC21XX",
            "SDCC_CYGNAL",
            "SOFTUNE_MB91460",
            "SOFTUNE_MB96340",
            "TASKING_ARM_CM4F",
            "TEMPLATE",
            "CDK_THEAD_CK802",
            "XCC_XTENSA",
            "WIZC_PIC18",
        ],
        "heap": ["1", "2", "3", "4", "5"],
        # FreeRTOSConfig.h options
        "allow_unprivileged_critical_sections": [True, False],
        "application_allocated_heap": [True, False],
        "assert": [None, "ANY"],
        "check_for_stack_overflow": ["0", "1", "2"],
        "check_handler_installation": [True, False],
        "cpu_clock_hz": ["ANY"],
        "enable_access_control_list": [True, False],
        "enable_backward_compatibility": [True, False],
        "enable_fpu": [True, False],
        "enable_heap_protector": [True, False],
        "enable_mpu": [True, False],
        "enable_mve": [True, False],
        "enable_trustzone": [True, False],
        "enforce_system_calls_from_kernel_only": [True, False],
        "generate_run_time_stats": [True, False],
        "heap_clear_memory_on_free": [True, False],
        "idle_should_yield": [True, False],
        "include_application_defined_privileged_functions": [True, False],
        "include_eTaskGetState": [True, False],
        "include_uxTaskPriorityGet": [True, False],
        "include_uxTaskGetStackHighWaterMark": [True, False],
        "include_vTaskDelay": [True, False],
        "include_vTaskDelayUntil": [True, False],
        "include_vTaskDelete": [True, False],
        "include_vTaskPrioritySet": [True, False],
        "include_vTaskSuspend": [True, False],
        "include_xEventGroupSetBitFromISR": [True, False],
        "include_xResumeFromISR": [True, False],
        "include_xTaskAbortDelay": [True, False],
        "include_xTaskGetCurrentTaskHandle": [True, False],
        "include_xTaskGetIdleTaskHandle": [True, False],
        "include_xTaskGetHandle": [True, False],
        "include_xTaskGetSchedulerState": [True, False],
        "include_xTaskResumeFromISR": [True, False],
        "include_xTimerPendFunctionCall": [True, False],
        "kernel_interrupt_priority": ["ANY"],
        "kernel_provided_static_memory": [True, False],
        "max_api_call_interrupt_priority": ["ANY"],
        "max_co_routine_priorities": ["ANY"],
        "max_priorities": ["ANY"],
        "max_task_name_len": ["ANY"],
        "max_secure_contexts": ["ANY"],
        "max_syscall_interrupt_priority": ["ANY"],
        "message_buffer_length_type": ["ANY"],
        "minimal_stack_size": ["ANY"],
        "num_thread_local_storage_pointers": ["ANY"],
        "number_of_cores": ["ANY"],
        "protected_kernel_object_pool_size": ["ANY"],
        "queue_registry_size": ["ANY"],
        "risc_v_chip_extension": ["Pulpino_Vega_RV32M1RM", "RISCV_MTIME_CLINT_no_extensions", "RISCV_no_extensions", "RV32I_CLINT_no_extensions"],
        "run_freertos_secure_only": [True, False],
        "run_multiple_priorities": [True, False],
        "stack_allocation_from_separate_heap": [True, False],
        "stack_depth_type": ["ANY"],
        "stats_buffer_max_length": ["ANY"],
        "support_dynamic_allocation": [True, False],
        "support_static_allocation": [True, False],
        "system_call_stack_size": ["ANY"],
        "systick_clock_hz": [None, "ANY"],
        "task_default_core_affinity": ["ANY"],
        "task_notification_array_entries": ["ANY"],
        "tex_s_c_b_flash": ["ANY"],
        "tex_s_c_b_sram": ["ANY"],
        "tick_rate_hz": ["ANY"],
        "tick_type_width_in_bits": ["ANY"],
        "timer_queue_length": ["ANY"],
        "timer_service_task_core_affinity": ["ANY"],
        "timer_task_priority": ["ANY"],
        "timer_task_stack_depth": ["ANY"],
        "total_heap_size": ["ANY"],
        "total_mpu_regions": ["ANY"],
        "use_application_task_tag": [True, False],
        "use_co_routines": [True, False],
        "use_core_affinity": [True, False],
        "use_counting_semaphores": [True, False],
        "use_daemon_task_startup_hook": [True, False],
        "use_event_groups": [True, False],
        "use_idle_hook": [True, False],
        "use_malloc_failed_hook": [True, False],
        "use_mini_list_item": [True, False],
        "use_mpu_wrappers_v1": [True, False],
        "use_mutexes": [True, False],
        "use_newlib_reentrant": [True, False],
        "use_passive_idle_hook": [True, False],
        "use_port_optimised_task_selection": [True, False],
        "use_preemption": [True, False],
        "use_queue_sets": [True, False],
        "use_recursive_mutexes": [True, False],
        "use_sb_completed_callback": [True, False],
        "use_stats_formatting_functions": [True, False],
        "use_stream_buffers": [True, False],
        "use_task_notifications": [True, False],
        "use_task_preemption_disable": [True, False],
        "use_tick_hook": [True, False],
        "use_tickless_idle": [True, False],
        "use_time_slicing": [True, False],
        "use_timers": [True, False],
        "use_trace_facility": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
        "port": "GCC_POSIX",
        "heap": "4",
        # FreeRTOSConfig.h options
        "allow_unprivileged_critical_sections": True,
        "application_allocated_heap": True,
        "assert": "configASSERT( x ) if( ( x ) == 0 ) { taskDISABLE_INTERRUPTS(); for( ; ; ) ; }",
        "check_for_stack_overflow": 0,
        "check_handler_installation": True,
        "cpu_clock_hz": 60_000_000,
        "enable_access_control_list": True,
        "enable_backward_compatibility": False,
        "enable_fpu": True,
        "enable_heap_protector": False,
        "enable_mpu": True,
        "enable_mve": True,
        "enable_trustzone": True,
        "enforce_system_calls_from_kernel_only": True,
        "generate_run_time_stats": False,
        "heap_clear_memory_on_free": True,
        "idle_should_yield": True,
        "include_application_defined_privileged_functions": False,
        "include_eTaskGetState": False,
        "include_uxTaskGetStackHighWaterMark": False,
        "include_uxTaskPriorityGet": True,
        "include_vTaskDelay": True,
        "include_vTaskDelayUntil": True,
        "include_vTaskDelete": True,
        "include_vTaskPrioritySet": True,
        "include_vTaskSuspend": True,
        "include_xEventGroupSetBitFromISR": True,
        "include_xResumeFromISR": True,
        "include_xTaskAbortDelay": False,
        "include_xTaskGetCurrentTaskHandle": True,
        "include_xTaskGetIdleTaskHandle": False,
        "include_xTaskGetHandle": False,
        "include_xTaskGetSchedulerState": True,
        "include_xTaskResumeFromISR": True,
        "include_xTimerPendFunctionCall": False,
        "kernel_interrupt_priority": 0,
        "kernel_provided_static_memory": True,
        "max_api_call_interrupt_priority": 0,
        "max_co_routine_priorities": 1,
        "max_priorities": 5,
        "max_secure_contexts": 5,
        "max_syscall_interrupt_priority": 0,
        "max_task_name_len": 16,
        "message_buffer_length_type": "size_t",
        "minimal_stack_size": 128,
        "num_thread_local_storage_pointers": 5,
        "number_of_cores": 1,
        "protected_kernel_object_pool_size": 10,
        "queue_registry_size": 10,
        "risc_v_chip_extension": "RISCV_no_extensions",
        "run_freertos_secure_only": True,
        "run_multiple_priorities": False,
        "stack_allocation_from_separate_heap": False,
        "stack_depth_type": "uint16_t",
        "stats_buffer_max_length": "0xFFFF",
        "support_dynamic_allocation": True,
        "support_static_allocation": True,
        "system_call_stack_size": 128,
        "systick_clock_hz": None,
        "task_default_core_affinity": "tskNO_AFFINITY",
        "task_notification_array_entries": 3,
        "tex_s_c_b_flash": "0x07UL",
        "tex_s_c_b_sram": "0x07UL",
        "tick_rate_hz": 250,
        "tick_type_width_in_bits": "TICK_TYPE_WIDTH_16_BITS",
        "timer_queue_length": 10,
        "timer_service_task_core_affinity": "tskNO_AFFINITY",
        "timer_task_priority": 3,
        "timer_task_stack_depth": 128,
        "total_heap_size": 10_240,
        "total_mpu_regions": 8,
        "use_application_task_tag": False,
        "use_co_routines": False,
        "use_core_affinity": False,
        "use_counting_semaphores": False,
        "use_daemon_task_startup_hook": False,
        "use_event_groups": True,
        "use_idle_hook": False,
        "use_malloc_failed_hook": False,
        "use_mini_list_item": True,
        "use_mpu_wrappers_v1": False,
        "use_mutexes": False,
        "use_newlib_reentrant": False,
        "use_passive_idle_hook": False,
        "use_port_optimised_task_selection": False,
        "use_preemption": True,
        "use_queue_sets": False,
        "use_recursive_mutexes": False,
        "use_sb_completed_callback": False,
        "use_stats_formatting_functions": False,
        "use_stream_buffers": True,
        "use_task_notifications": True,
        "use_task_preemption_disable": False,
        "use_tick_hook": False,
        "use_tickless_idle": False,
        "use_time_slicing": False,
        "use_timers": True,
        "use_trace_facility": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
        if self.settings.os in ["Linux", "Macos"]:
            self.options.port = "GCC_POSIX"
        elif self.settings.os == "Windows":
            self.options.port = "MSVC_MINGW"

    def configure(self):
        if self.options.shared or self.settings.os == "baremetal":
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

        if self.options.port not in ["GCC_RISC_V_GENERIC", "IAR_RISC_V_GENERIC"]:
            self.options.rm_safe("risc_v_chip_extension")
        else:
            if self.options.port == "IAR_RISC_V_GENERIC":
                self.options.risc_v_chip_extension = "RV32I_CLINT_no_extensions"

    def validate(self):
        if self.options.port == "IAR_RISC_V_GENERIC" and self.options.get_safe("risc_v_chip_extension") != "RV32I_CLINT_no_extensions":
            raise ConanInvalidConfiguration("Only the RV32I_CLINT_no_extensions RISC-V extension can be enabled when using the IAR_RISC_V_GENERIC port")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "FreeRTOSConfig.h", self.recipe_folder, self.export_sources_folder)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["FREERTOS_HEAP"] = self.options.heap
        tc.variables["FREERTOS_PORT"] = self.options.port
        if self.options.get_safe("risc_v_chip_extension"):
            tc.variables["FREERTOS_RISCV_EXTENSION"] = self.options.risc_v_chip_extension
        tc.variables["_FREERTOS_CONFIG_DIR"] = self.build_folder.replace("\\", "/")
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        copy(self, "FreeRTOSConfig.h", self.export_sources_folder, self.build_folder)
        for option, value in self.options.items():
            if str(option) in ["fPIC", "heap", "port", "shared"]:
                continue
            if str(option) == "systick_clock_hz":
                if  value is None:
                    replace_in_file(
                        self, os.path.join(self.build_folder, "FreeRTOSConfig.h"), "@systick_clock_hz@", ""
                    )
                else:
                    replace_in_file(
                        self, os.path.join(self.build_folder, "FreeRTOSConfig.h"), "@systick_clock_hz@", f"#define configSYSTICK_CLOCK_HZ {value}"
                    )
                continue
            if str(option) == "assert":
                if  value is None:
                    replace_in_file(
                        self, os.path.join(self.build_folder, "FreeRTOSConfig.h"), "@assert@", ""
                    )
                else:
                    replace_in_file(
                        self, os.path.join(self.build_folder, "FreeRTOSConfig.h"), "@assert@", f"#define {value}"
                    )
                continue

            key = f"@{str(option)}@"
            if value in ["True", "true"]:
                value = "1"
            elif value in ["False", "false"]:
                value = "0"
            replace_in_file(
                self, os.path.join(self.build_folder, "FreeRTOSConfig.h"), key, value
            )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(
            self,
            "*.h",
            os.path.join(self.source_folder, "include"),
            os.path.join(self.package_folder, "include"),
            keep_path=False,
        )
        if self.options.get_safe("risc_v_chip_extension"):
            for risc_v_generic_port in ["GCC", "IAR"]:
                port_include_directories[f"{risc_v_generic_port}_RISC_V_GENERIC"].append(
                    os.path.join(
                        risc_v_generic_port,
                        "RISC-V",
                        "chip_specific_extensions",
                        str(self.options.risc_v_chip_extension),
                    ))
        for include_directory in port_include_directories[str(self.options.port)]:
            copy(
                self,
                "*.h",
                os.path.join(self.source_folder, "portable", include_directory),
                os.path.join(self.package_folder, "include"),
                keep_path=False,
            )
        copy(
            self,
            "*freertos_kernel.dll",
            self.build_folder,
            os.path.join(self.package_folder, "bin"),
        )
        copy(
            self,
            "*freertos_kernel.lib",
            self.build_folder,
            os.path.join(self.package_folder, "lib"),
        )
        copy(
            self,
            "*freertos_kernel.so*",
            self.build_folder,
            os.path.join(self.package_folder, "lib"),
        )
        copy(
            self,
            "*freertos_kernel.dylib",
            self.build_folder,
            os.path.join(self.package_folder, "lib"),
        )
        copy(
            self,
            "*freertos_kernel.a",
            self.build_folder,
            os.path.join(self.package_folder, "lib"),
        )
        copy(
            self,
            "LICENSE.md",
            self.source_folder,
            os.path.join(self.package_folder, "licenses"),
        )
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["freertos_kernel"]

        if self.settings.os in ["FreeBSD", "Linux"]:
            self.cpp_info.system_libs.append("pthread")
