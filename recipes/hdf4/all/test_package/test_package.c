#include <hdf.h>

#define FILE_NAME      "General_HDFobjects.hdf"
#define VG_NAME        "AN Vgroup"
#define FILE_LABEL_TXT "General HDF objects"
#define FILE_DESC_TXT  "This is an HDF file that contains general HDF objects"
#define DATA_LABEL_TXT "Common AN Vgroup"
#define DATA_DESC_TXT  "This is a vgroup that is used to test data annotations"

int main() {
  /************************* Variable declaration **************************/

  intn   status_n;     /* returned status for functions returning an intn  */
  int32  status_32,    /* returned status for functions returning an int32 */
         file_id,      /* HDF file identifier */
         an_id,        /* AN interface identifier */
         file_label_id,  /* file label identifier */
         file_desc_id,   /* file description identifier */
         data_label_id,  /* data label identifier */
         data_desc_id,   /* data description identifier */
         vgroup_id;
  uint16 vgroup_tag, vgroup_ref;

  /********************** End of variable declaration **********************/

  /*
   * Create the HDF file.
   */
  file_id = Hopen(FILE_NAME, DFACC_CREATE, 0);

  /*
   * Initialize the AN interface.
   */
  an_id = ANstart(file_id);

  /*
   * Create the file label.
   */
  file_label_id = ANcreatef(an_id, AN_FILE_LABEL);

  /*
   * Write the annotations to the file label.
   */
  status_32 = ANwriteann(file_label_id, FILE_LABEL_TXT, (int32) strlen(FILE_LABEL_TXT));

  /*
   * Create file description.
   */
  file_desc_id = ANcreatef(an_id, AN_FILE_DESC);

  /*
   * Write the annotation to the file description.  
   */
  status_32 = ANwriteann(file_desc_id, FILE_DESC_TXT, (int32) strlen(FILE_DESC_TXT));

  /*
   * Create a vgroup in the V interface.  Note that the vgroup's ref number 
   * is set to -1 for creating and the access mode is "w" for writing.
   */
  status_n = Vstart(file_id);
  vgroup_id = Vattach(file_id, -1, "w");
  status_32 = Vsetname(vgroup_id, VG_NAME);

  /*
   * Obtain the tag and ref number of the vgroup for subsequent
   * references.  
   */
  vgroup_tag = (uint16) VQuerytag(vgroup_id);
  vgroup_ref = (uint16) VQueryref(vgroup_id);

  /*
   * Create the data label for the vgroup identified by its tag 
   * and ref number.
   */
  data_label_id = ANcreate(an_id, vgroup_tag, vgroup_ref, AN_DATA_LABEL);

  /*
   * Write the annotation text to the data label.
   */
  status_32 = ANwriteann(data_label_id, DATA_LABEL_TXT, (int32) strlen(DATA_LABEL_TXT));

  /*
   * Create the data description for the vgroup identified by its tag 
   * and ref number.
   */
  data_desc_id = ANcreate(an_id, vgroup_tag, vgroup_ref, AN_DATA_DESC);

  /*
   * Write the annotation text to the data description.
   */
  status_32 = ANwriteann(data_desc_id, DATA_DESC_TXT, (int32) strlen(DATA_DESC_TXT));

  /*
   * Teminate access to the vgroup and to the V interface.
   */
  status_32 = Vdetach(vgroup_id);
  status_n = Vend(file_id);

  /*
   * Terminate access to each annotation explicitly.
   */
  status_n = ANendaccess(file_label_id);
  status_n = ANendaccess(file_desc_id);
  status_n = ANendaccess(data_label_id);
  status_n = ANendaccess(data_desc_id);

  /*
   * Terminate access to the AN interface and close the HDF file.
   */
  status_32 = ANend(an_id);
  status_n = Hclose(file_id);

  return 0;
}
