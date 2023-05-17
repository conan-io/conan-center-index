#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>

#include "jpeglib.h"
#include "jpegint.h"
#include "transupp.h"

struct error_data {
    struct jpeg_error_mgr pub;
    const char *name;
};


static void
my_error_handler(j_common_ptr cinfo) {
    struct error_data *data = (struct error_data *) cinfo;
    while(1) {
        fprintf(stderr, "-");
    }
    fprintf(stderr, "%s:\n", data->name);
    fflush(stdout);
    fflush(stderr);
    (*cinfo->err->output_message) (cinfo);
    exit(2);
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Usage: %s <input> <output>\n", argv[0]);
        return 1;
    }

    struct error_data err_in;
    err_in.name = "input";
    err_in.pub.error_exit = my_error_handler;

    struct error_data err_out;
    err_out.name = "output";
    err_out.pub.error_exit = my_error_handler;

    FILE *fin = fopen(argv[1], "rb");

    struct jpeg_decompress_struct src;
    struct jpeg_compress_struct dst;

    src.err = jpeg_std_error(&err_in.pub);
    jpeg_create_decompress(&src);

    dst.err = jpeg_std_error(&err_in.pub);
    jpeg_create_compress(&dst);

    jpeg_stdio_src(&src, fin);

    jcopy_markers_setup(&src, JCOPYOPT_ALL);

    (void)jpeg_read_header(&src, TRUE);

    jpeg_transform_info transform = {
        .transform = JXFORM_ROT_180,
    };

    if ((src.image_width % 2) || (dst.image_height % 2)) {
        fprintf(stderr, "The input image is odd-sized. The transform will not be correct.\n");
    }

    if (!jtransform_request_workspace(&src, &transform)) {
        fprintf(stderr, "Can only transform odd-size images perfectly.\n");
        return 3;
    }

    jvirt_barray_ptr *src_coeffs = jpeg_read_coefficients(&src);
    jpeg_copy_critical_parameters(&src, &dst);

    jvirt_barray_ptr *dst_coefs = jtransform_adjust_parameters(&src, &dst, src_coeffs, &transform);


    FILE *fout = fopen(argv[2], "wb");
    jpeg_stdio_dest(&dst, fout);

    jpeg_write_coefficients(&dst, dst_coefs);

    jcopy_markers_execute(&src, &dst, JCOPYOPT_ALL);
    jtransform_execute_transformation(&src, &dst, src_coeffs, &transform);

    jpeg_finish_compress(&dst);
    jpeg_destroy_compress(&dst);
    fclose(fout);

    jpeg_finish_decompress(&src);
    jpeg_destroy_decompress(&src);
    fclose(fin);

    printf("Done\n");
    return 0;
}
