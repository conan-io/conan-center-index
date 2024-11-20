/*
 * Copyright (c) 2017-2019 Dmitry Marakasov <amdmi3@amdmi3.ru>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

#include <assert.h>
#include <libversion/version.h>

int main() {
    /* 0.99 < 1.11 */
    assert(version_compare2("0.99", "1.11") == -1);

    /* 1.0 == 1.0.0 */
    assert(version_compare2("1.0", "1.0.0") == 0);

    /* 1.0alpha1 < 1.0.rc1 */
    assert(version_compare2("1.0alpha1", "1.0.rc1") == -1);

    /* 1.0 > 1.0.rc1 */
    assert(version_compare2("1.0", "1.0-rc1") == 1);

    /* 1.2.3alpha4 is the same as 1.2.3~a4 */
    assert(version_compare2("1.2.3alpha4", "1.2.3~a4") == 0);

    /* by default, `p' is treated as `pre'... */
    assert(version_compare2("1.0p1", "1.0pre1") == 0);
    assert(version_compare2("1.0p1", "1.0post1") == -1);
    assert(version_compare2("1.0p1", "1.0patch1") == -1);

    /* ...but this is tunable: here it's handled as `patch` */
    assert(version_compare4("1.0p1", "1.0pre1", VERSIONFLAG_P_IS_PATCH, 0) == 1);
    assert(version_compare4("1.0p1", "1.0post1", VERSIONFLAG_P_IS_PATCH, 0) == 0);
    assert(version_compare4("1.0p1", "1.0patch1", VERSIONFLAG_P_IS_PATCH, 0) == 0);

    /* a way to check that the version belongs to a given release */
    assert(
        (version_compare4("1.0alpha1", "1.0", 0, VERSIONFLAG_LOWER_BOUND) == 1) &&
        (version_compare4("1.0alpha1", "1.0", 0, VERSIONFLAG_UPPER_BOUND) == -1) &&
        (version_compare4("1.0.1", "1.0", 0, VERSIONFLAG_LOWER_BOUND) == 1) &&
        (version_compare4("1.0.1", "1.0", 0, VERSIONFLAG_UPPER_BOUND) == -1)
        /* 1.0alpha1 and 1.0.1 belong to 1.0 release, e.g. they lie between
           (lowest possible version in 1.0) and (highest possible version in 1.0) */
    );
}
