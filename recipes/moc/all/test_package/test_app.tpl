@# Template for the moc compiler.
@{if exists MODULE 
@{    foreach my-class in ALL_CLASSES
@{        if ( is-from-current-module ) && ( ! is-a Interface ) && exists bizObject
@{            if ! exists BizObjIntfDir
@>                set BizObjIntfDir=bizobj/@(:lowercase-all @(Name))
@}            end if ! exists BizObjIntfDir
@{            if ! exists BizObjIntfPkg
@>                set BizObjIntfPkg=bizobj/@(:lowercase-all @(Name)).h
@}            end if ! exists BizObjIntfPkg
@{            if ! exists BizObjDefineGuards
@>                set BizObjDefineGuards=@(:uppercase-all bizobj_@(:uppercase-all @(Name))
@}            end if ! exists BizObjDefineGuards
@# ///////////////////////////////////////////////
@# //
@# //
@# //
@# //
@# //
@# //
@# //
@# ///////////////////////////////////////////////
@{            open include/@(BizObjIntfDir)/@(Name).h
#ifndef @(BizObjDefineGuards)
#define @(BizObjDefineGuards)

class @(Name) @(:if exists HasParents :then :              @\
@(:format-list : suffix-sep=',' :foreach parent in parents @\
                                        : public @(Name))  @\
) {
public:
@{                foreach property in properties
    /**The @(Name) property - @(description). */
    @(Type.TypeString) @(Name);
@}                end foreach property in properties
};
#endif // @(BizObjDefineGuards)
@}            end open include/@(BizObjIntfDir)/@(Name).h
@# ///////////////////////////////////////////////
@}        end if is-from-current-module
@}    end foreach my-class in ALL_CLASSES
@}endif exists MODULE
