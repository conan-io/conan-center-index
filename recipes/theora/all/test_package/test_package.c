/********************************************************************
 *                                                                  *
 * THIS FILE IS PART OF THE OggTheora SOFTWARE CODEC SOURCE CODE.   *
 * USE, DISTRIBUTION AND REPRODUCTION OF THIS LIBRARY SOURCE IS     *
 * GOVERNED BY A BSD-STYLE SOURCE LICENSE INCLUDED WITH THIS SOURCE *
 * IN 'COPYING'. PLEASE READ THESE TERMS BEFORE DISTRIBUTING.       *
 *                                                                  *
 * THE Theora SOURCE CODE IS COPYRIGHT (C) 2002-2010                *
 * by the Xiph.Org Foundation and contributors http://www.xiph.org/ *
 *                                                                  *
 ********************************************************************
  function: example of querying various library parameters.
  last mod: $Id$
 ********************************************************************/

#ifdef HAVE_CONFIG_H
# include <config.h>
#endif

#include <stdio.h>
#include <stdlib.h>

#include "theora/theoraenc.h"


/* Print the library's bitstream version number
   This is the highest supported bitstream version number,
   not the version number of the implementation itself. */
int print_version(void)
{
    unsigned version = th_version_number();

    fprintf(stdout, "Bitstream: %d.%d.%d (0x%06X)\n",
        (version >> 16) & 0xff, (version >> 8) & 0xff, (version) & 0xff,
        version);

    return 0;
}

/* Print the library's own version string
   This is generally the same at the vendor string embedded
   in encoded files. */
int print_version_string(void)
{
    const char *version = th_version_string();

    if (version == NULL) {
      fprintf(stderr, "Error querying libtheora version string.\n");
      return -1;
    }

    fprintf(stdout, "Version: %s\n", version);

    return 0;
}

/* Generate a dummy encoder context for use in th_encode_ctl queries */
th_enc_ctx *dummy_encode_ctx(void)
{
    th_enc_ctx *ctx;
    th_info info;

    /* set the minimal video parameters */
    th_info_init(&info);
    info.frame_width=320;
    info.frame_height=240;
    info.fps_numerator=1;
    info.fps_denominator=1;

    /* allocate and initialize a context object */
    ctx = th_encode_alloc(&info);
    if (ctx == NULL) {
        fprintf(stderr, "Error allocating encoder context.\n");
    }

    /* clear the info struct */
    th_info_clear(&info);

    return ctx;
}

/* Query the current and maximum values for the 'speed level' setting.
   This can be used to ask the encoder to trade off encoding quality
   vs. performance cost, for example to adapt to realtime constraints. */
int check_speed_level(th_enc_ctx *ctx, int *current, int *max)
{
    int ret;

    /* query the current speed level */
    ret = th_encode_ctl(ctx, TH_ENCCTL_GET_SPLEVEL, current, sizeof(int));
    if (ret) {
        fprintf(stderr, "Error %d getting current speed level.\n", ret);
        return ret;
    }
    /* query the maximum speed level, which varies by encoder version */
    ret = th_encode_ctl(ctx, TH_ENCCTL_GET_SPLEVEL_MAX, max, sizeof(int));
    if (ret) {
        fprintf(stderr, "Error %d getting max speed level.\n", ret);
        return ret;
    }

    return 0;
}

/* Print the current and maximum speed level settings */
int print_speed_level(th_enc_ctx *ctx)
{
    int current = -1;
    int max = -1;
    int ret;

    ret = check_speed_level(ctx, &current, &max);
    if (ret == 0) {
        fprintf(stdout, "Default speed level: %d\n", current);
        fprintf(stdout, "Maximum speed level: %d\n", max);
    }

    return ret;
}

int main(int argc, char **argv) {
    th_enc_ctx *ctx;

    /* print versioning */
    print_version_string();
    print_version();

    /* allocate a generic context for queries that require it */
    ctx = dummy_encode_ctx();
    if (ctx != NULL) {
        /* dump the speed level setting */
        print_speed_level(ctx);
        /* clean up */
        th_encode_free(ctx);
    }

    return 0;
}
