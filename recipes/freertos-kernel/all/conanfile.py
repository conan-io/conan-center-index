import os
import textwrap

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, save

required_conan_version = ">=1.60.0"



default_configs = {
    "GCC_POSIX": textwrap.dedent("""\
        #ifndef FREERTOS_CONFIG_H
        #define FREERTOS_CONFIG_H

        #define configUSE_PREEMPTION                       1
        #define configUSE_PORT_OPTIMISED_TASK_SELECTION    0
        #define configUSE_IDLE_HOOK                        1
        #define configUSE_TICK_HOOK                        1
        #define configUSE_DAEMON_TASK_STARTUP_HOOK         1
        #define configTICK_RATE_HZ                         ( 1000 )
        #define configMINIMAL_STACK_SIZE                   ( ( unsigned short ) PTHREAD_STACK_MIN )
        #define configTOTAL_HEAP_SIZE                      ( ( size_t ) ( 65 * 1024 ) )
        #define configMAX_TASK_NAME_LEN                    ( 12 )
        #define configUSE_TRACE_FACILITY                   1
        #define configUSE_16_BIT_TICKS                     0
        #define configIDLE_SHOULD_YIELD                    1
        #define configUSE_MUTEXES                          1
        #define configCHECK_FOR_STACK_OVERFLOW             0
        #define configUSE_RECURSIVE_MUTEXES                1
        #define configQUEUE_REGISTRY_SIZE                  20
        #define configUSE_APPLICATION_TASK_TAG             1
        #define configUSE_COUNTING_SEMAPHORES              1
        #define configUSE_ALTERNATIVE_API                  0
        #define configUSE_QUEUE_SETS                       1
        #define configUSE_TASK_NOTIFICATIONS               1
        #define configSUPPORT_STATIC_ALLOCATION            1
        #define configRECORD_STACK_HIGH_ADDRESS            1

        #define configUSE_TIMERS                           1
        #define configTIMER_TASK_PRIORITY                  ( configMAX_PRIORITIES - 1 )
        #define configTIMER_QUEUE_LENGTH                   20
        #define configTIMER_TASK_STACK_DEPTH               ( configMINIMAL_STACK_SIZE * 2 )

        #define configMAX_PRIORITIES                       ( 7 )

        unsigned long ulGetRunTimeCounterValue( void );
        void vConfigureTimerForRunTimeStats( void );
        #define configGENERATE_RUN_TIME_STATS             1

        #define configUSE_CO_ROUTINES                     0
        #define configMAX_CO_ROUTINE_PRIORITIES           ( 2 )

        #define configUSE_STATS_FORMATTING_FUNCTIONS      0

        #define configSTACK_DEPTH_TYPE                    uint32_t

        #define INCLUDE_vTaskPrioritySet                  1
        #define INCLUDE_uxTaskPriorityGet                 1
        #define INCLUDE_vTaskDelete                       1
        #define INCLUDE_vTaskCleanUpResources             0
        #define INCLUDE_vTaskSuspend                      1
        #define INCLUDE_vTaskDelayUntil                   1
        #define INCLUDE_vTaskDelay                        1
        #define INCLUDE_uxTaskGetStackHighWaterMark       1
        #define INCLUDE_uxTaskGetStackHighWaterMark2      1
        #define INCLUDE_xTaskGetSchedulerState            1
        #define INCLUDE_xTimerGetTimerDaemonTaskHandle    1
        #define INCLUDE_xTaskGetIdleTaskHandle            1
        #define INCLUDE_xTaskGetHandle                    1
        #define INCLUDE_eTaskGetState                     1
        #define INCLUDE_xSemaphoreGetMutexHolder          1
        #define INCLUDE_xTimerPendFunctionCall            1
        #define INCLUDE_xTaskAbortDelay                   1

        extern void vAssertCalled( const char * const pcFileName,
                                unsigned long ulLine );

        #define configASSERT( x )    if( ( x ) == 0 ) vAssertCalled( __FILE__, __LINE__ )

        #define configUSE_MALLOC_FAILED_HOOK    1

        #define configMAC_ISR_SIMULATOR_PRIORITY    ( configMAX_PRIORITIES - 1 )

        extern void vLoggingPrintf( const char * pcFormatString,
                                    ... );

        #endif /* FREERTOS_CONFIG_H */
    """),
   "MSVC_MINGW": textwrap.dedent("""\
        #ifndef FREERTOS_CONFIG_H
        #define FREERTOS_CONFIG_H

        #define configUSE_PREEMPTION					1
        #define configUSE_PORT_OPTIMISED_TASK_SELECTION	1
        #define configUSE_IDLE_HOOK						1
        #define configUSE_TICK_HOOK						1
        #define configUSE_DAEMON_TASK_STARTUP_HOOK		1
        #define configTICK_RATE_HZ						( 1000 )
        #define configMINIMAL_STACK_SIZE				( ( unsigned short ) 70 )
        #define configTOTAL_HEAP_SIZE					( ( size_t ) ( 49 * 1024 ) )
        #define configMAX_TASK_NAME_LEN					( 12 )
        #define configUSE_TRACE_FACILITY				1
        #define configUSE_16_BIT_TICKS					0
        #define configIDLE_SHOULD_YIELD					1
        #define configUSE_MUTEXES						1
        #define configCHECK_FOR_STACK_OVERFLOW			0
        #define configUSE_RECURSIVE_MUTEXES				1
        #define configQUEUE_REGISTRY_SIZE				20
        #define configUSE_MALLOC_FAILED_HOOK			1
        #define configUSE_APPLICATION_TASK_TAG			1
        #define configUSE_COUNTING_SEMAPHORES			1
        #define configUSE_ALTERNATIVE_API				0
        #define configUSE_QUEUE_SETS					1
        #define configUSE_TASK_NOTIFICATIONS			1
        #define configTASK_NOTIFICATION_ARRAY_ENTRIES		5
        #define configSUPPORT_STATIC_ALLOCATION			1
        #define configINITIAL_TICK_COUNT				( ( TickType_t ) 0 )
        #define configSTREAM_BUFFER_TRIGGER_LEVEL_TEST_MARGIN 1

        #define configUSE_TIMERS						1
        #define configTIMER_TASK_PRIORITY				( configMAX_PRIORITIES - 1 )
        #define configTIMER_QUEUE_LENGTH				20
        #define configTIMER_TASK_STACK_DEPTH			( configMINIMAL_STACK_SIZE * 2 )

        #define configMAX_PRIORITIES					( 7 )

        #define configRUN_TIME_COUNTER_TYPE				uint64_t
        configRUN_TIME_COUNTER_TYPE ulGetRunTimeCounterValue( void );
        void vConfigureTimerForRunTimeStats( void );
        #define configGENERATE_RUN_TIME_STATS			1
        #define portCONFIGURE_TIMER_FOR_RUN_TIME_STATS() vConfigureTimerForRunTimeStats()
        #define portGET_RUN_TIME_COUNTER_VALUE() ulGetRunTimeCounterValue()

        #define configUSE_CO_ROUTINES 					1
        #define configMAX_CO_ROUTINE_PRIORITIES			( 2 )

        #define configUSE_STATS_FORMATTING_FUNCTIONS	1

        #define INCLUDE_vTaskPrioritySet				1
        #define INCLUDE_uxTaskPriorityGet				1
        #define INCLUDE_vTaskDelete						1
        #define INCLUDE_vTaskCleanUpResources			0
        #define INCLUDE_vTaskSuspend					1
        #define INCLUDE_vTaskDelayUntil					1
        #define INCLUDE_vTaskDelay						1
        #define INCLUDE_uxTaskGetStackHighWaterMark		1
        #define INCLUDE_xTaskGetSchedulerState			1
        #define INCLUDE_xTimerGetTimerDaemonTaskHandle	1
        #define INCLUDE_xTaskGetIdleTaskHandle			1
        #define INCLUDE_xTaskGetHandle					1
        #define INCLUDE_eTaskGetState					1
        #define INCLUDE_xSemaphoreGetMutexHolder		1
        #define INCLUDE_xTimerPendFunctionCall			1
        #define INCLUDE_xTaskAbortDelay					1

        extern void vAssertCalled( unsigned long ulLine, const char * const pcFileName );
        #define configASSERT( x ) if( ( x ) == 0 ) vAssertCalled( __LINE__, __FILE__ )

        #endif /* FREERTOS_CONFIG_H */
    """),
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
            "GCC_ARM_CA53_64_BIT",
            "GCC_ARM_CA53_64_BIT_SRE",
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
            "CDK_THEAD_CK802",
            "XCC_XTENSA",
            "WIZC_PIC18",
        ],
        "heap": ["1", "2", "3", "4", "5"],
        "config": ["ANY"],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
        "port": "GCC_POSIX",
        "heap": "4",
        "config": default_configs["GCC_POSIX"],
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared or self.settings.os == "baremetal":
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

        if self.settings.os in ["Linux", "Macos"]:
            self.options.port = "GCC_POSIX"
            self.options.config = default_configs["GCC_POSIX"]
        elif self.settings.os == "Windows":
            self.options.port = "MSVC_MINGW"
            self.options.config = default_configs["MSVC_MINGW"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["FREERTOS_HEAP"] = self.options.heap
        tc.cache_variables["FREERTOS_PORT"] = self.options.port
        tc.variables["_FREERTOS_CONFIG_DIR"] = self.export_sources_folder
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        save(self, os.path.join(self.export_sources_folder, "FreeRTOSConfig.h"), str(self.options.config))

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "*.h", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"), keep_path=False)
        copy(self, "*freertos_kernel.dll", self.build_folder, os.path.join(self.package_folder, "bin"))
        copy(self, "*freertos_kernel.lib", self.build_folder, os.path.join(self.package_folder, "lib"))
        copy(self, "*freertos_kernel.so*", self.build_folder, os.path.join(self.package_folder, "lib"))
        copy(self, "*freertos_kernel.dylib", self.build_folder, os.path.join(self.package_folder, "lib"))
        copy(self, "*freertos_kernel.a", self.build_folder, os.path.join(self.package_folder, "lib"))
        copy(self, "LICENSE.md", self.source_folder, os.path.join(self.package_folder, "licenses"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["freertos_kernel"]

        if self.settings.os in ["FreeBSD", "Linux"]:
            self.cpp_info.system_libs.append("pthread")
