#define STBI_WINDOWS_UTF8

#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"

#define STB_DEFINE
#include "stb.h"

float hdr_data[200][200][3];

void dummy_write(void* context, void* data, int len)
{
    static char dummy[1024];
    if (len > 1024)
        len = 1024;
    memcpy(dummy, data, len);
}

int main(int argc, char** argv)
{
    int w, h;

    if (argc > 1) {
        int i, n;

        for (i = 1; i < argc; ++i) {
            int res;
            int w2, h2, n2;
            unsigned char* data;
            printf("%s\n", argv[i]);
            res = stbi_info(argv[i], &w2, &h2, &n2);
            data = stbi_load(argv[i], &w, &h, &n, 0);
            if (data)
                free(data);
            else
                printf("Failed &n\n");
            data = stbi_load(argv[i], &w, &h, &n, 4);
            if (data)
                free(data);
            else
                printf("Failed &n\n");
            data = stbi_load(argv[i], &w, &h, 0, 1);
            if (data)
                free(data);
            else
                printf("Failed 1\n");
            data = stbi_load(argv[i], &w, &h, 0, 2);
            if (data)
                free(data);
            else
                printf("Failed 2\n");
            data = stbi_load(argv[i], &w, &h, 0, 3);
            if (data)
                free(data);
            else
                printf("Failed 3\n");
            data = stbi_load(argv[i], &w, &h, &n, 4);
            assert(data);
            assert(w == w2 && h == h2 && n == n2);
            assert(res);
            if (data) {
                char fname[512];
                stb_splitpath(fname, argv[i], STB_FILE);
                stbi_write_png(stb_sprintf("output/%s.png", fname), w, h, 4, data, w * 4);
                stbi_write_bmp(stb_sprintf("output/%s.bmp", fname), w, h, 4, data);
                stbi_write_tga(stb_sprintf("output/%s.tga", fname), w, h, 4, data);
                stbi_write_png_to_func(dummy_write, 0, w, h, 4, data, w * 4);
                stbi_write_bmp_to_func(dummy_write, 0, w, h, 4, data);
                stbi_write_tga_to_func(dummy_write, 0, w, h, 4, data);
                free(data);
            } else
                printf("FAILED 4\n");
        }
    } else {
        int i;
#ifdef PNGSUITE_PRIMARY
        char** files = stb_readdir_files("pngsuite/primary");
#else
        char** files = stb_readdir_files("images");
#endif
        for (i = 0; i < stb_arr_len(files); ++i) {
            int n;
            char** failed = NULL;
            unsigned char* data;
            printf(".");
            data = stbi_load(files[i], &w, &h, &n, 0);
            if (data)
                free(data);
            else
                stb_arr_push(failed, "&n");
            data = stbi_load(files[i], &w, &h, 0, 1);
            if (data)
                free(data);
            else
                stb_arr_push(failed, "1");
            data = stbi_load(files[i], &w, &h, 0, 2);
            if (data)
                free(data);
            else
                stb_arr_push(failed, "2");
            data = stbi_load(files[i], &w, &h, 0, 3);
            if (data)
                free(data);
            else
                stb_arr_push(failed, "3");
            data = stbi_load(files[i], &w, &h, 0, 4);
            if (data)
                ;
            else
                stb_arr_push(failed, "4");
            if (data) {
                char fname[512];

#ifdef PNGSUITE_PRIMARY
                int w2, h2;
                unsigned char* data2;
                stb_splitpath(fname, files[i], STB_FILE_EXT);
                data2 = stbi_load(stb_sprintf("pngsuite/primary_check/%s", fname), &w2, &h2, 0, 4);
                if (!data2)
                    printf("FAILED: couldn't load 'pngsuite/primary_check/%s\n", fname);
                else {
                    if (w != w2 || h != w2 || 0 != memcmp(data, data2, w * h * 4)) {
                        int x, y, c;
                        if (w == w2 && h == h2)
                            for (y = 0; y < h; ++y)
                                for (x = 0; x < w; ++x)
                                    for (c = 0; c < 4; ++c)
                                        assert(data[y * w * 4 + x * 4 + c] == data2[y * w * 4 + x * 4 + c]);
                        printf("FAILED: %s loaded but didn't match PRIMARY_check 32-bit version\n", files[i]);
                    }
                    free(data2);
                }
#else
                stb_splitpath(fname, files[i], STB_FILE);
                stbi_write_png(stb_sprintf("output/%s.png", fname), w, h, 4, data, w * 4);
#endif
                free(data);
            }
            if (failed) {
                int j;
                printf("FAILED: ");
                for (j = 0; j < stb_arr_len(failed); ++j)
                    printf("%s ", failed[j]);
                printf(" -- %s\n", files[i]);
            }
        }
        printf("Tested %d files.\n", i);
    }
    return 0;
}
