#include <measflow.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    const char *path = "test_conan.meas";

    /* Write a small file */
    MeasWriter *w = meas_writer_open(path);
    if (!w) {
        fprintf(stderr, "Failed to create writer\n");
        return 1;
    }
    MeasGroupWriter *g = meas_writer_add_group(w, "TestGroup");
    MeasChannelWriter *ch = meas_group_add_channel(g, "Signal", MEAS_FLOAT32);
    float data[] = {1.0f, 2.0f, 3.0f};
    meas_channel_write_f32(ch, data, 3);
    meas_writer_close(w);

    /* Read it back */
    MeasReader *r = meas_reader_open(path);
    if (!r) {
        fprintf(stderr, "Failed to open reader\n");
        return 1;
    }
    const MeasGroupData *grp = meas_reader_group_by_name(r, "TestGroup");
    if (!grp) {
        fprintf(stderr, "Group not found\n");
        meas_reader_close(r);
        return 1;
    }
    const MeasChannelData *rch = meas_group_channel_by_name(grp, "Signal");
    if (!rch || rch->sample_count != 3) {
        fprintf(stderr, "Channel mismatch\n");
        meas_reader_close(r);
        return 1;
    }
    float buf[3];
    meas_channel_read_f32(rch, buf, 3);
    meas_reader_close(r);
    remove(path);

    printf("MeasFlow Conan package test OK (wrote and read 3 samples)\n");
    return 0;
}
