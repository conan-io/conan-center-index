#include <id3v2lib-2.0/id3v2lib.h>
#include <stdio.h>

int main(void) {
  ID3v2_Tag *tag = ID3v2_Tag_new_empty();
  ID3v2_Tag_set_title(tag, "Amazing Song!");

  ID3v2_TextFrame *title_frame = ID3v2_Tag_get_title_frame(tag);
  printf("Track title: %s\n", title_frame->data->text);

  ID3v2_Tag_free(tag);
  return 0;
}
