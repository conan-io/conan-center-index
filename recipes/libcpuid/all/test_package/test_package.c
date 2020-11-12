#include "libcpuid/libcpuid.h"

#include <stdio.h>

int main(void)
{
	if (!cpuid_present()) {                                                // check for CPUID presence
		printf("Sorry, your CPU doesn't support CPUID!\n");
		return -1;
	}


	struct cpu_raw_data_t raw;                                             // contains only raw data
	struct cpu_id_t data;                                                  // contains recognized CPU features data


	if (cpuid_get_raw_data(&raw) < 0) {                                    // obtain the raw CPUID data
		printf("Sorry, cannot get the CPUID raw data.\n");
		printf("Error: %s\n", cpuid_error());                          // cpuid_error() gives the last error description
		return -2;
	}


	if (cpu_identify(&raw, &data) < 0) {                                   // identify the CPU, using the given raw data.
		printf("Sorrry, CPU identification failed.\n");
		printf("Error: %s\n", cpuid_error());
		return -3;
	}


	printf("Found: %s CPU\n", data.vendor_str);                            // print out the vendor string (e.g. `GenuineIntel')
	printf("Processor model is `%s'\n", data.cpu_codename);                // print out the CPU code name (e.g. `Pentium 4 (Northwood)')
	printf("The full brand string is `%s'\n", data.brand_str);             // print out the CPU brand string
	printf("The processor has %dK L1 cache and %dK L2 cache\n",
		data.l1_data_cache, data.l2_cache);                            // print out cache size information
	printf("The processor has %d cores and %d logical processors\n",
		data.num_cores, data.num_logical_cpus);                        // print out CPU cores information

	printf("Supported multimedia instruction sets:\n");
	printf("  MMX         : %s\n", data.flags[CPU_FEATURE_MMX] ? "present" : "absent");
	printf("  MMX-extended: %s\n", data.flags[CPU_FEATURE_MMXEXT] ? "present" : "absent");
	printf("  SSE         : %s\n", data.flags[CPU_FEATURE_SSE] ? "present" : "absent");
	printf("  SSE2        : %s\n", data.flags[CPU_FEATURE_SSE2] ? "present" : "absent");
	printf("  3DNow!      : %s\n", data.flags[CPU_FEATURE_3DNOW] ? "present" : "absent");

	printf("CPU clock is: %d MHz (according to your OS)\n",
		cpu_clock_by_os());                                            // print out the CPU clock, according to the OS
	printf("CPU clock is: %d MHz (tested)\n", cpu_clock_measure(200, 0));  // print out the CPU clock, measured with RDTSC.

	return 0;
}
