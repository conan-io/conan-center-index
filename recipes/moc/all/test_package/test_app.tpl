@# Template for the moc compiler.
@# ///////////////////////////////////////////////
@# //
@# // Used for sample test_app
@# //
@# ///////////////////////////////////////////////
@{if exists MODULE 
@# ///////////////////////////////////////////////
@# //
@# //  First iterate over all the classes 
@# //  and setup some additional key/value properties
@# //  to use in the rest of the following template patterns.
@# //  
@# ///////////////////////////////////////////////
@{        foreach my-class in ALL_CLASSES
@{            if ( is-from-current-module ) && ( ! is-a Interface ) && exists bizObject
@{                foreach method in methods
@{			if ! exists description
@>                         set description=""
@}			end if ! exists description
@{                      foreach a in in-arguments
@{                          if ! exists description
@>                             set description=""
@}                          end if ! exists description
@}                      end foreach a in in-arguments
@{                      foreach ex in error-arguments
@{                          if ! exists description
@>                              set description=""
@}                          end if ! exists description
@}                      end foreach ex in error-arguments
@}                end foreach method in methods
@{                foreach p in properties
@{                    if ! exists description
@>                        set description=""
@}                    end if ! exists description
@}                end foreach p in properties
@{		  if ! exists _Package
@>		      set _Package=bizobj
@}		  end if ! exists _Package
@{		  if ! exists _TasksPackage
@>		      set _TasksPackage=bizprocess
@}		  end if ! exists _Package
@{		  if ! exists BizObjIntfDir
@> 		      set BizObjIntfDir=@(_Package)/@(:lowercase-all @(Name))
@}		  end if ! exists BizObjIntfDir
@{		  if ! exists BizObjIntfPkg
@> 		      set BizObjIntfPkg=@(_Package)/@(:lowercase-all @(Name)).h
@}		  end if ! exists BizObjIntfPkg
@{		  if ! exists BizObjDefineGuards
@> 		      set BizObjDefineGuards=@(:uppercase-all @(_Package))_@(:uppercase-all @(Name))
@}		  end if ! exists BizObjDefineGuards
@{		  if ! exists BizTasksIntfDir
@> 		      set BizTasksIntfDir=@(_TasksPackage)/@(:lowercase-all @(Name))tasks
@}		  end if ! exists BizTasksIntfDir
@{		  if ! exists BizTasksIntfPkg
@> 		      set BizTasksIntfPkg=@(_TasksPackage)/@(:lowercase-all @(Name))tasks.h
@}		  end if ! exists BizTasksIntfPkg
@{		  if ! exists BizObjImplDir
@> 		      set BizObjImplDir=src/@(_Package)/@(:lowercase-all @(Name))
@}		  end if ! exists BizObjImplDir
@{		  if ! exists BizObjImplPkg
@> 		      set BizObjImplPkg=@(_Package)/@(:lowercase-all @(Name))
@}		  end if ! exists BizObjImplPkg
@{		  if ! exists BizTasksImplDir
@> 		      set BizTasksImplDir=src/@(_TasksPackage)/@(:lowercase-all @(Name))tasks
@}		  end if ! exists BizTasksImplDir
@{		  if ! exists BizTasksImplPkg
@> 		      set BizTasksImplPkg=@(_TasksPackage)/@(:lowercase-all @(Name))tasks
@}		  end if ! exists BizTasksImplPkg
@# ///////////////////////////////////////////////
@# //
@# //
@# //
@# //
@# //
@# //
@# //
@# ///////////////////////////////////////////////
@{    		  open include/@(BizObjIntfDir)/@(Name).h
#ifndef @(BizObjDefineGuards)
#define @(BizObjDefineGuards)

@{                    if exists HEADER_CODE
#line @(HEADER_CODE.Lineno) "@(HEADER_CODE.Filename)" 
@(HEADER_CODE)
#line @(OUTPUT_NEXT_LINENO) "@(OUTPUT_FILENAME)" 
@}                    endif exists HEADER_CODE

@{        foreach my-type in ALL_TYPES
@{            if exists header_name
@{                if ! exists "file::@(header_name)Inc_Hdr"
@>                    set file::@(header_name)Inc_Hdr=1
#include @(Header)
@}                end if exists file::@(header_name)Inc_Hdr
@}            end if  exists "Header"
@}        end foreach my-type in ALL_TYPES
/**
 * <P>
 * @(Name)
 * a @(Name).
@{            if exists description
 *   @(description);
@}
 * </P>
 *
 * @@version $Id$
 */
class @(Name) @(:if exists HasParents :then : @\
@(:format-list : suffix-sep=',' :foreach parent in parents : public @(Name))@\
) {
public:
@{                foreach m in methods
    /**@(description)
@{                    foreach in-arg in in-arguments
     * @@param @(Name) - @(description)
@}                    end foreach in-arg in in-arguments
     * @@return @(ReturnType) 
@{                    foreach ex in error-arguments
     * @@exception @(Name)
@}                    end foreach ex in error-arguments
     */
    public @(ReturnType) @(Name)( @(:format-list : suffix-sep=',' :foreach a in in-arguments : @(Type.TypeString) @(Name)) )
	throws  @(:if ! empty "error-arguments" :then noexcept(false) :else noexcept ) ;
@}                end foreach m in methods
private:
@{                foreach property in properties
    /**The @(Name) property - @(description). */
    @(Type.TypeString) @(Name);
@}                end foreach property in properties
};

@{                    if exists HEADER_END_CODE
#line @(HEADER_END_CODE.Lineno) "@(HEADER_END_CODE.Filename)" 
@(HEADER_END_CODE)
#line @(OUTPUT_NEXT_LINENO) "@(OUTPUT_FILENAME)" 
@}                    endif exists HEADER_END_CODE

#endif // @(BizObjDefineGuards)
@}    		  end open include/@(BizObjIntfDir)/@(Name).h
@# ///////////////////////////////////////////////
@# //
@# //
@# //      The @(Name).cpp implementation file
@# //
@# //
@# //
@# //
@# ///////////////////////////////////////////////
@{		  open @(BizObjImplDir)/@(Name).cpp
#include "@(BizObjIntfDir)/@(Name).h"


@(Name)::@(Name)() :
     @(:format-list : suffix-sep=','                           @\
                    :foreach p in parents     : @(Name)()      @\
                    :foreach p in properties  : @(Name)()      @\
     )
{
}

@{                    if exists SOURCE_CODE
#line @(SOURCE_CODE.Lineno) "@(SOURCE_CODE.Filename)" 
@(SOURCE_CODE)
#line @(OUTPUT_NEXT_LINENO) "@(OUTPUT_FILENAME)" 
@}                    endif
@}		  end open @(BizObjImplDir)/@(Name).cpp
@# ///////////////////////////////////////////////
@# //
@# //
@# //
@# //
@# //
@# //
@# //
@# ///////////////////////////////////////////////
@{		  open @(BizObjImplDir)/@(Name).ddl.sample

DROP TABLE db@(Name);


/** The db@(Name) table stores the @(Name) entries. 
 * @(description).
 *
@{                    foreach i in inherited-properties  properties
@{                        if ( exists dbcol )
 *	@(dbcol) - @(description)
@}                        end if ( exists dbcol )
@}                    end foreach i in inherited-properties properties
 */
CREATE TABLE db@(Name) (
@{                    foreach i in inherited-properties properties
@{                        if ( exists dbcol )
	@(dbcol) @(Type.dbcoltype),
@}                        end if ( exists dbcol )
@}                    end foreach i in inherited-properties properties
	PRIMARY KEY(id)
);

CREATE UNIQUE INDEX db@(Name)_idx0 ON db@(Name)(id);

INSERT INTO dbDatabaseId 
    ( id, db_table, db_column, min, max, idx_value, class_id )
  values
    ( '@(BizObjImplPkg).@(Name)Bean',
      'db@(Name)', 'id', 1000, 1000000, 1000, NULL )
;

@}		  end open @(BizObjImplDir)/@(Name).ddl.sample
@}            end if is-from-current-module
@}        end foreach my-class in ALL_CLASSES
@}endif exists MODULE
