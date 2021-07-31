#include <cpu_features_macros.h>
#if defined(CPU_FEATURES_ARCH_X86)
#include <cpuinfo_x86.h>
#elif defined(CPU_FEATURES_ARCH_ARM)
#include <cpuinfo_arm.h>
#elif defined(CPU_FEATURES_ARCH_AARCH64)
#include <cpuinfo_aarch64.h>
#elif defined(CPU_FEATURES_ARCH_MIPS)
#include <cpuinfo_mips.h>
#elif defined(CPU_FEATURES_ARCH_PPC)
#include <ccpuinfo_ppc.h>
#endif

#include <stdlib.h>
#include <stdio.h>

int main()
{
#if defined(CPU_FEATURES_ARCH_X86)
    X86Features features = GetX86Info().features;
#elif defined(CPU_FEATURES_ARCH_ARM)
    ArmFeatures features = GetArmInfo().features;
#elif defined(CPU_FEATURES_ARCH_AARCH64)
    Aarch64Features features = GetAarch64Info().features;
#elif defined(CPU_FEATURES_ARCH_MIPS)
    MipsFeatures features = GetMipsInfo().features;
#elif defined(CPU_FEATURES_ARCH_PPC)
    PPCFeatures features = GetPPCInfo().features;
#endif

#if defined(CPU_FEATURES_ARCH_X86) || defined(CPU_FEATURES_ARCH_ARM) || defined(CPU_FEATURES_ARCH_AARCH64)
    printf("AES is%s available\n", features.aes ? "" : "n't");
#elif defined(CPU_FEATURES_ARCH_MIPS)
    printf("EVA is%s available\n", features.eva ? "" : "n't");
#elif defined(CPU_FEATURES_ARCH_PPC)
    printf("SPE is%s available\n", features.spe ? "" : "n't");
#endif

    return EXIT_SUCCESS;
}
