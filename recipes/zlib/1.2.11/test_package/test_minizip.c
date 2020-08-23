#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include <zip.h>
#include <unzip.h>
#ifdef _WIN32
    #include <iowin32.h>
#endif

/* TODO: create test for this header */
#include <mztools.h>

const char text[] = ""
"Conveying or northward offending admitting perfectly my. Colonel gravity get thought fat smiling add but. Wonder twenty hunted and put income set desire expect. Am cottage calling my is mistake cousins talking up. Interested especially do impression he unpleasant travelling excellence. All few our knew time done draw ask.\n"
"\n"
"Village did removed enjoyed explain nor ham saw calling talking. Securing as informed declared or margaret. Joy horrible moreover man feelings own shy. Request norland neither mistake for yet. Between the for morning assured country believe. On even feet time have an no at. Relation so in confined smallest children unpacked delicate. Why sir end believe uncivil respect. Always get adieus nature day course for common. My little garret repair to desire he esteem.\n"
""
"As it so contrasted oh estimating instrument. Size like body some one had. Are conduct viewing boy minutes warrant expense. Tolerably behaviour may admitting daughters offending her ask own. Praise effect wishes change way and any wanted. Lively use looked latter regard had. Do he it part more last in. Merits ye if mr narrow points. Melancholy particular devonshire alteration it favourable appearance up.\n"
""
"Extremity direction existence as dashwoods do up. Securing marianne led welcomed offended but offering six raptures. Conveying concluded newspaper rapturous oh at. Two indeed suffer saw beyond far former mrs remain. Occasional continuing possession we insensible an sentiments as is. Law but reasonably motionless principles she. Has six worse downs far blush rooms above stood.\n"
""
"Comfort reached gay perhaps chamber his six detract besides add. Moonlight newspaper up he it enjoyment agreeable depending. Timed voice share led his widen noisy young. On weddings believed laughing although material do exercise of. Up attempt offered ye civilly so sitting to. She new course get living within elinor joy. She her rapturous suffering concealed.\n"
""
"Neat own nor she said see walk. And charm add green you these. Sang busy in this drew ye fine. At greater prepare musical so attacks as on distant. Improving age our her cordially intention. His devonshire sufficient precaution say preference middletons insipidity. Since might water hence the her worse. Concluded it offending dejection do earnestly as me direction. Nature played thirty all him.\n"
""
"Mr do raising article general norland my hastily. Its companions say uncommonly pianoforte favourable. Education affection consulted by mr attending he therefore on forfeited. High way more far feet kind evil play led. Sometimes furnished collected add for resources attention. Norland an by minuter enquire it general on towards forming. Adapted mrs totally company two yet conduct men.\n"
""
"An sincerity so extremity he additions. Her yet there truth merit. Mrs all projecting favourable now unpleasing. Son law garden chatty temper. Oh children provided to mr elegance marriage strongly. Off can admiration prosperous now devonshire diminution law.\n"
""
"He share of first to worse. Weddings and any opinions suitable smallest nay. My he houses or months settle remove ladies appear. Engrossed suffering supposing he recommend do eagerness. Commanded no of depending extremity recommend attention tolerably. Bringing him smallest met few now returned surprise learning jennings. Objection delivered eagerness he exquisite at do in. Warmly up he nearer mr merely me.\n"
""
"Yet remarkably appearance get him his projection. Diverted endeavor bed peculiar men the not desirous. Acuteness abilities ask can offending furnished fulfilled sex. Warrant fifteen exposed ye at mistake. Blush since so in noisy still built up an again. As young ye hopes no he place means. Partiality diminution gay yet entreaties admiration. In mr it he mention perhaps attempt pointed suppose. Unknown ye chamber of warrant of norland arrived.\n"
"";

const char* zip_fname = "test_minizip.zip";

int print_zip_info(unzFile);
void Display64BitsSize(ZPOS64_T, int);

int main(int argc, char** argv) {
    /* Zip */
    printf("---------- Create ZIP ----------\n");

    zipFile zf = zipOpen64(zip_fname, APPEND_STATUS_CREATE);
    if (zf == NULL) {
        printf("Error in zipOpen64, fname: %s\n", zip_fname);
        exit(EXIT_FAILURE);
    }

    int res;
    zip_fileinfo zfi = {0};
    res = zipOpenNewFileInZip64(zf, "fname.bin", &zfi, NULL, 0, NULL, 0, NULL, Z_DEFLATED, Z_BEST_COMPRESSION, 0);
    if (res != ZIP_OK) {
        printf("Error in zipOpenNewFileInZip64, code: %d\n", res);
        exit(EXIT_FAILURE);
    }

    res = zipWriteInFileInZip(zf, text, sizeof(text));
    if (res != ZIP_OK) {
        printf("Error in zipWriteInFileInZip, code: %d\n", res);
        exit(EXIT_FAILURE);
    }

    res = zipCloseFileInZip(zf);
    if (res != ZIP_OK) {
        printf("Error in zipCloseFileInZip, code: %d\n", res);
        exit(EXIT_FAILURE);
    }

    res = zipClose(zf, "Test MiniZip");
    if(res != ZIP_OK) {
        printf("Error in zipClose, code: %d\n", res);
        exit(EXIT_FAILURE);
    }

    printf("ZIP file created, name: %s\n", zip_fname);

    /* unZip */
    printf("---------- Test unZIP ----------\n");

    unzFile unzf = unzOpen64(zip_fname);
    if (unzf == NULL) {
        printf("Error in unzOpen64, fname: %s\n", zip_fname);
        exit(EXIT_FAILURE);
    }

    res = print_zip_info(unzf);
    if (res != UNZ_OK) {
        printf("Read ZIP info error, code: %d\n", res);
        exit(EXIT_FAILURE);
    }

    res = unzGoToFirstFile(unzf);
    if (res != UNZ_OK) {
        printf("Error in unzGoToFirstFile, code: %d\n", res);
        exit(EXIT_FAILURE);
    }

    unz_file_info64 unz_fi = {0};
    res = unzGetCurrentFileInfo64(unzf, &unz_fi, NULL, 0, NULL, 0, NULL, 0);
    if (res != UNZ_OK) {
        printf("Error in unzGetCurrentFileInfo64, code: %d\n", res);
        exit(EXIT_FAILURE);
    }

    /* Compare size */
    if (unz_fi.uncompressed_size != (ZPOS64_T) sizeof(text)) {
        printf("Error in Zip, failed compare size. In Zip => %llu, source size => %llu\n", unz_fi.uncompressed_size, (ZPOS64_T) sizeof(text));
        exit(EXIT_FAILURE);
    }

    res = unzOpenCurrentFile(unzf);
    if (res != UNZ_OK) {
        printf("Error in unzOpenCurrentFile, code: %d\n", res);
        exit(EXIT_FAILURE);
    }

    char* read_data = calloc(1, sizeof(text));
    if (read_data == NULL) {
        printf("Can`t allocate read buffer\n");
        exit(EXIT_FAILURE);
    }

    res = unzReadCurrentFile(unzf, read_data, sizeof(text));
    if (res < 0) {
        printf("Error in unzReadCurrentFile, code: %d\n", res);
        exit(EXIT_FAILURE);
    }

    if (memcmp(text, read_data, sizeof(text)) != 0) {
        printf("Error in zip, source and uncompressed data not equal.\n");
        exit(EXIT_FAILURE);
    }

    res = unzClose(unzf);
    if (res != UNZ_OK) {
        printf("Error in unzClose, code: %d\n", res);
        exit(EXIT_FAILURE);
    }

    printf("Zip / Unzip OK\n");
    free(read_data);
    return EXIT_SUCCESS;
}

int print_zip_info(unzFile unzf) {
    char comment[256] = {0};
    int res;
    res = unzGetGlobalComment(unzf, comment, sizeof(comment));
    if (res < 0) {
        printf("Error in unzGetGlobalComment, code: %d\n", res);
        return  res;
    }
    printf("unZIP. Global comment => %s\n", comment);

    res = unzGoToFirstFile(unzf);
    if (res != UNZ_OK) {
        printf("Error in unzGoToFirstFile, code: %d\n", res);
        return res;
    }

    unz_global_info64 gi = {0};
    res = unzGetGlobalInfo64(unzf, &gi);
    if (res != UNZ_OK) {
        printf("Error in unzGetGlobalInfo64, code: %d\n", res);
        return res;
    }
    printf("  Length  Method     Size Ratio   Date    Time   CRC-32     Name\n");
    printf("  ------  ------     ---- -----   ----    ----   ------     ----\n");

    for (uLong i = 0; i < gi.number_entry; i++) {
        unz_file_info64 file_info = {0};
        char fname_inzip[256] = {0};
        res = unzGetCurrentFileInfo64(unzf, &file_info, fname_inzip, sizeof(fname_inzip), NULL, 0, NULL, 0);
        if (res != UNZ_OK) {
            printf("Error in unzGetCurrentFileInfo64, code: %d\n", res);
            return res;
        }

        uLong ratio = 0;
        if (file_info.uncompressed_size>0) {
            ratio = (uLong) ((file_info.compressed_size*100) / file_info.uncompressed_size);
        }

        char crypt = ' ';
        if ((file_info.flag & 1) != 0) {
            char crypt = '*';
        }

        const char* str_method = NULL;
        if (file_info.compression_method==0) {
            str_method = "Stored";
        } else if (file_info.compression_method == Z_DEFLATED) {
            uInt iLevel=(uInt) ((file_info.flag & 0x6) / 2);
            if (iLevel == 0) {
              str_method = "Defl:N";
            } else if (iLevel == 1) {
              str_method = "Defl:X";
            } else if ((iLevel == 2) || (iLevel == 3)) {
              str_method="Defl:F"; /* 2:fast , 3 : extra fast*/
            }
        } else if (file_info.compression_method==Z_BZIP2ED) {
              str_method="BZip2 ";
        } else {
            str_method="Unkn. ";
        }

        Display64BitsSize(file_info.uncompressed_size, 7);
        printf("  %6s%c", str_method, crypt);
        Display64BitsSize(file_info.compressed_size, 7);
        printf(" %3lu%%  %2.2lu-%2.2lu-%2.2lu  %2.2lu:%2.2lu  %8.8lx   %s\n",
                ratio,
                (uLong) file_info.tmu_date.tm_mon + 1,
                (uLong) file_info.tmu_date.tm_mday,
                (uLong) file_info.tmu_date.tm_year - 1900,
                (uLong) file_info.tmu_date.tm_hour,
                (uLong) file_info.tmu_date.tm_min,
                (uLong) file_info.crc,
                fname_inzip
        );
        if ((i + 1) < gi.number_entry) {
            res = unzGoToNextFile(unzf);
            if (res != UNZ_OK) {
                printf("Error in unzGoToNextFile, code: %d\n", res);
                return res;
            }
        }
    }

    return UNZ_OK;
}

void Display64BitsSize(ZPOS64_T n, int size_char) {
    /* to avoid compatibility problem , we do here the conversion */
    char number[21] = {0};
    int offset = 19;
    int pos_string = 19;
    number[20] = 0;

    for (;;) {
        number[offset] = (char) ((n % 10) + '0');
      if (number[offset] != '0') {
          pos_string = offset;
      }
      n /= 10;
      if (offset == 0) {
          break;
      }
      offset--;
  }

  int size_display_string = 19 - pos_string;
  while (size_char > size_display_string) {
          size_char--;
          printf(" ");
   }

  printf("%s", &number[pos_string]);
}

