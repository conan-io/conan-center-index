// SPDX-License-Identifier: LGPL-3.0
/**
 * @file    example_build_config.c
 * @author  向阳 (hinata.hoshino@foxmail.com)
 * @brief   不同对齐方式下的格式化的例子
 * @version 1.0
 * @date    2023-07-23
 *
 * @copyright Copyright (c) 向阳, all rights reserved.
 *
 */
#include "mtfmt.h"
#include <stdint.h>
#include <stdio.h>

/**
 * @brief 测试1个位是否被set
 *
 */
#define BIT_TEST(v, b) (!!(((v) & (b)) == (b)))

/**
 * @brief 把boolean变成C字符串
 *
 */
#define BOOL2STR(b)    ((b) ? "true" : "false")

int main(void)
{
    uint32_t cfg = MSTR_CONFIGURE_CFG_VAL(mstr_configure());
    uint32_t compiler = MSTR_CONFIGURE_CC_VAL(cfg);

    puts("+-----------+--------------------------+-------+");

    const char* compiler_name = "unknown";
    switch (compiler) {
    case MSTR_BUILD_CC_MSVC: compiler_name = "msvc"; break;
    case MSTR_BUILD_CC_GNUC: compiler_name = "gcc"; break;
    case MSTR_BUILD_CC_ARMCC: compiler_name = "armcc"; break;
    case MSTR_BUILD_CC_ARMCLANG: compiler_name = "armclang"; break;
    case MSTR_BUILD_CC_EMSCRIPTEN: compiler_name = "emscripten"; break;
    case MSTR_BUILD_CC_OTHER: compiler_name = "unknown"; break;
    }
    printf("| Compiler  | %-24s |  ---  |\n", compiler_name);

    puts("+-----------+--------------------------+-------+");

    printf(
        "| Configure | %-24s | %5s |\n",
        "_MSTR_USE_MALLOC",
        BOOL2STR(BIT_TEST(cfg, MSTRCFG_USE_MALLOC_BIT))
    );
    printf(
        "|           | %-24s | %5s |\n",
        "_MSTR_BUILD_DLL",
        BOOL2STR(BIT_TEST(cfg, MSTRCFG_BUILD_DLL_BIT))
    );
    printf(
        "|           | %-24s | %5s |\n",
        "_MSTR_USE_HARDWARE_DIV",
        BOOL2STR(BIT_TEST(cfg, MSTRCFG_BUILD_HARDWARE_DIV))
    );
    printf(
        "|           | %-24s | %5s |\n",
        "_MSTR_USE_STD_IO",
        BOOL2STR(BIT_TEST(cfg, MSTRCFG_USE_STD_IO))
    );
    printf(
        "|           | %-24s | %5s |\n",
        "_MSTR_USE_UTF_8",
        BOOL2STR(BIT_TEST(cfg, MSTRCFG_USE_UTF_8))
    );
    printf(
        "|           | %-24s | %5s |\n",
        "_MSTR_USE_CPP_EXCEPTION",
        BOOL2STR(BIT_TEST(cfg, MSTRCFG_USE_CXX_EXCEPTION))
    );
    printf(
        "|           | %-24s | %5s |\n",
        "_MSTR_USE_FP_FLOAT32",
        BOOL2STR(BIT_TEST(cfg, MSTRCFG_USE_FLOAT32))
    );
    printf(
        "|           | %-24s | %5s |\n",
        "_MSTR_USE_FP_FLOAT64",
        BOOL2STR(BIT_TEST(cfg, MSTRCFG_USE_FLOAT64))
    );
    printf(
        "|           | %-24s | %5s |\n",
        "_MSTR_USE_ALLOC",
        BOOL2STR(BIT_TEST(cfg, MSTRCFG_USE_ALLOCATOR))
    );

    puts("+-----------+--------------------------+-------+");

    return 0;
}
