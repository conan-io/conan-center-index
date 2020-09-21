/*
  in-memory.c -- modify zip file in memory
  Copyright (C) 2014-2015 Dieter Baron and Thomas Klausner

  This file is part of libzip, a library to manipulate ZIP archives.
  The authors can be contacted at <libzip@nih.at>

  Redistribution and use in source and binary forms, with or without
  modification, are permitted provided that the following conditions
  are met:
  1. Redistributions of source code must retain the above copyright
     notice, this list of conditions and the following disclaimer.
  2. Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in
     the documentation and/or other materials provided with the
     distribution.
  3. The names of the authors may not be used to endorse or promote
     products derived from this software without specific prior
     written permission.

  THIS SOFTWARE IS PROVIDED BY THE AUTHORS ``AS IS'' AND ANY EXPRESS
  OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
  ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY
  DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
  DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
  GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
  IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
  OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
  IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "zip.h"

int
main(int argc, char *argv[])
{
    zip_source_t *src;
    zip_t *za;
    zip_error_t error;
    const char data [] = {"conan-center-index"};
    const size_t size = sizeof(data);
    char buffer [256] = {0};

    zip_error_init(&error);
    /* create source from buffer */
    if ((src = zip_source_buffer_create(data, size, 1, &error)) == NULL) {
        zip_error_fini(&error);
        return 1;
    }

    /* open zip archive from source */
    if ((za = zip_open_from_source(src, 0, &error)) == NULL) {
        zip_error_fini(&error);
        return 0;
    }
    zip_error_fini(&error);

    /* we'll want to read the data back after zip_close */
    zip_source_keep(src);


    /* close archive */
    if (zip_close(za) < 0) {
        return 1;
    }


    /* copy new archive to buffer */

    if (zip_source_is_deleted(src)) {
    }
    else {
        zip_stat_t zst;

        if (zip_source_stat(src, &zst) < 0) {
            return 1;
        }

        if (zip_source_open(src) < 0) {
            return 1;
        }

        if ((zip_uint64_t)zip_source_read(src, buffer, zst.size) < zst.size) {
            zip_source_close(src);
            return 1;
        }
        zip_source_close(src);
    }

    /* we're done with src */
    zip_source_free(src);

    return 0;
}
