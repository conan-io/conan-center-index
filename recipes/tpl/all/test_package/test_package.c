// https://github.com/troydhanson/tpl/blob/f8138ad393f4b1985c916029ab6d703e4e7a1c4c/tests/test1.c
//
// Copyright (c) 2005-2013, Troy Hanson    http://troydhanson.github.com/tpl/
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:
//
//     * Redistributions of source code must retain the above copyright
//       notice, this list of conditions and the following disclaimer.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
// IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
// TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
// PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
// OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
// EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
// PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
// PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
// LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
// NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
// SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#include <stdio.h>
#include <stdlib.h>
#include "tpl.h"

int main() {
    tpl_node *tn;
    int i,j=-1;
    void *addr;
    size_t sz;

    tn = tpl_map("i",&i);
    i=1;
    tpl_pack(tn,0);
    tpl_dump(tn,TPL_MEM,&addr,&sz);
    tpl_free(tn);

    tn = tpl_map("i",&j);
    tpl_load(tn,TPL_MEM,addr,sz);
    tpl_unpack(tn,0);
    printf("j is %d\n", j);
    tpl_free(tn);
    free(addr);
    return(0);
}
