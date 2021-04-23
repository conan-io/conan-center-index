/* test_package.c -- determine the maximum size of inflate's Huffman code tables over
 * all possible valid and complete Huffman codes, subject to a length limit.
 * Copyright (C) 2007, 2008, 2012 Mark Adler
 * Version 1.4  18 August 2012  Mark Adler
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#define local static

typedef unsigned long long big_t;
typedef unsigned long long code_t;
struct tab {
    size_t len;
    char * vec;
};

local int max;
local int root;
local int large;
local size_t size;
local int * code;
local big_t * num;
local struct tab * done;

#define INDEX(i, j, k)(((size_t)((i - 1) >> 1) * ((i - 2) >> 1) + (j >> 1) - 1) * (max - 1) + k - 1)

local void cleanup(void) {
    size_t n;

    if (done != NULL) {
        for (n = 0; n < size; n++)
            if (done[n].len)
                free(done[n].vec);
        free(done);
    }
    if (num != NULL)
        free(num);
    if (code != NULL)
        free(code);
}

local big_t count(int syms, int len, int left) {
    big_t sum;
    big_t got;
    int least;
    int most;
    int use;
    size_t index;

    if (syms == left)
        return 1;

    assert(syms > left && left > 0 && len < max);

    index = INDEX(syms, left, len);
    got = num[index];
    if (got)
        return got;

    least = (left << 1) - syms;
    if (least < 0)
        least = 0;

    most = (((code_t) left << (max - len)) - syms) /
        (((code_t) 1 << (max - len)) - 1);

    sum = 0;
    for (use = least; use <= most; use++) {
        got = count(syms - use, len + 1, (left - use) << 1);
        sum += got;
        if (got == (big_t) 0 - 1 || sum < got)
            return (big_t) 0 - 1;
    }

    assert(sum != 0);

    num[index] = sum;
    return sum;
}

local int beenhere(int syms, int len, int left, int mem, int rem) {
    size_t index;
    size_t offset;
    int bit;
    size_t length;
    char * vector;

    index = INDEX(syms, left, len);
    mem -= 1 << root;
    offset = (mem >> 3) + rem;
    offset = ((offset * (offset + 1)) >> 1) + rem;
    bit = 1 << (mem & 7);

    length = done[index].len;
    if (offset < length && (done[index].vec[offset] & bit) != 0)
        return 1;

    if (length <= offset) {

        if (length) {
            do {
                length <<= 1;
            } while (length <= offset);
            vector = realloc(done[index].vec, length);
            if (vector != NULL)
                memset(vector + done[index].len, 0, length - done[index].len);
        } else {
            length = 1 << (len - root);
            while (length <= offset)
                length <<= 1;
            vector = calloc(length, sizeof(char));
        }

        if (vector == NULL) {
            fputs("abort: unable to allocate enough memory\n", stderr);
            cleanup();
            exit(1);
        }

        done[index].len = length;
        done[index].vec = vector;
    }

    done[index].vec[offset] |= bit;
    return 0;
}

local void examine(int syms, int len, int left, int mem, int rem) {
    int least;
    int most;
    int use;

    if (syms == left) {

        code[len] = left;

        while (rem < left) {
            left -= rem;
            rem = 1 << (len - root);
            mem += rem;
        }
        assert(rem == left);

        if (mem > large) {
            large = mem;
            fflush(stdout);
        }

        code[len] = 0;
        return;
    }

    if (beenhere(syms, len, left, mem, rem))
        return;

    least = (left << 1) - syms;
    if (least < 0)
        least = 0;

    most = (((code_t) left << (max - len)) - syms) /
        (((code_t) 1 << (max - len)) - 1);

    use = least;
    while (rem < use) {
        use -= rem;
        rem = 1 << (len - root);
        mem += rem;
    }
    rem -= use;

    for (use = least; use <= most; use++) {
        code[len] = use;
        examine(syms - use, len + 1, (left - use) << 1,
            mem + (rem ? 1 << (len - root) : 0), rem << 1);
        if (rem == 0) {
            rem = 1 << (len - root);
            mem += rem;
        }
        rem--;
    }

    code[len] = 0;
}

local void enough(int syms) {
    int n;
    int left;
    size_t index;

    for (n = 0; n <= max; n++)
        code[n] = 0;

    large = 1 << root;
    if (root < max)
        for (n = 3; n <= syms; n++)
            for (left = 2; left < n; left += 2) {

                index = INDEX(n, left, root + 1);
                if (root + 1 < max && num[index])
                    examine(n, root + 1, left, 1 << root, 0);

                if (num[index - 1] && n <= left << 1)
                    examine((n - left) << 1, root + 1, (n - left) << 1,
                        1 << root, 0);
            }
}

int main(int argc, char ** argv) {

    int syms;
    int n;
    big_t got;
    big_t sum;
    code_t word;

    code = NULL;
    num = NULL;
    done = NULL;

    syms = 286;
    root = 9;
    max = 15;

    if (argc > 1) {
        syms = atoi(argv[1]);
        if (argc > 2) {
            root = atoi(argv[2]);
            if (argc > 3)
                max = atoi(argv[3]);
        }
    }
    if (argc > 4 || syms < 2 || root < 1 || max < 1) {
        fputs("invalid arguments, need: [sym >= 2 [root >= 1 [max >= 1]]]\n",
            stderr);
        return 1;
    }

    if (max > syms - 1)
        max = syms - 1;

    for (n = 0, word = 1; word; n++, word <<= 1)
    ;

    if (max > n || (code_t)(syms - 2) >= (((code_t) 0 - 1) >> (max - 1))) {
        fputs("abort: code length too long for internal types\n", stderr);
        return 1;
    }

    if ((code_t)(syms - 1) > ((code_t) 1 << max) - 1) {
        fprintf(stderr, "%d symbols cannot be coded in %d bits\n",
            syms, max);
        return 1;
    }

    code = calloc(max + 1, sizeof(int));
    if (code == NULL) {
        fputs("abort: unable to allocate enough memory\n", stderr);
        return 1;
    }

    if (syms == 2)
        num = NULL;
    else {
        size = syms >> 1;
        if (size > ((size_t) 0 - 1) / (n = (syms - 1) >> 1) ||
            (size *= n, size > ((size_t) 0 - 1) / (n = max - 1)) ||
            (size *= n, size > ((size_t) 0 - 1) / sizeof(big_t)) ||
            (num = calloc(size, sizeof(big_t))) == NULL) {
            fputs("abort: unable to allocate enough memory\n", stderr);
            cleanup();
            return 1;
        }
    }

    sum = 0;
    for (n = 2; n <= syms; n++) {
        got = count(n, 1, 2);
        sum += got;
        if (got == (big_t) 0 - 1 || sum < got) {
            fputs("abort: can't count that high!\n", stderr);
            cleanup();
            return 1;
        }
    }

    if (syms == 2)
        done = NULL;
    else if (size > ((size_t) 0 - 1) / sizeof(struct tab) ||
        (done = calloc(size, sizeof(struct tab))) == NULL) {
        fputs("abort: unable to allocate enough memory\n", stderr);
        cleanup();
        return 1;
    }

    if (root > max)
        root = max;
    if ((code_t) syms < ((code_t) 1 << (root + 1)))
        enough(syms);

    cleanup();
    return 0;
}
