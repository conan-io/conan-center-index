/*
 * ===========================================================================
 *
 *                            PUBLIC DOMAIN NOTICE
 *               National Center for Biotechnology Information
 *
 *  This software/database is a "United States Government Work" under the
 *  terms of the United States Copyright Act.  It was written as part of
 *  the author's official duties as a United States Government employee and
 *  thus cannot be copyrighted.  This software/database is freely available
 *  to the public for use. The National Library of Medicine and the U.S.
 *  Government have not placed any restriction on its use or reproduction.
 *
 *  Although all reasonable efforts have been taken to ensure the accuracy
 *  and reliability of the software and data, the NLM and the U.S.
 *  Government do not and cannot warrant the performance or results that
 *  may be obtained by using this software or data. The NLM and the U.S.
 *  Government disclaim all warranties, express or implied, including
 *  warranties of performance, merchantability or fitness for any particular
 *  purpose.
 *
 *  Please cite the author in any work or product based on this material.
 *
 * ===========================================================================
 *
 * File Description:
 *   Minimalistic application
 *
 */

#include <ncbi_pch.hpp>
#include <corelib/ncbiapp.hpp>
#include <corelib/ncbienv.hpp>
#include <corelib/ncbiargs.hpp>

USING_NCBI_SCOPE;


/////////////////////////////////////////////////////////////////////////////
//  CSampleBasicApplication::

class CSampleBasicApplication : public CNcbiApplication
{
private:
    virtual void Init(void);
    virtual int  Run(void);
    virtual void Exit(void);
};


/////////////////////////////////////////////////////////////////////////////
//  Init test for all different types of arguments

void CSampleBasicApplication::Init(void)
{
    // // Set error posting and tracing on maximum
    // SetDiagTrace(eDT_Enable);
    // SetDiagPostFlag(eDPF_All);
    // SetDiagPostLevel(eDiag_Info);

    // Create command-line argument descriptions class
    unique_ptr<CArgDescriptions> arg_desc(new CArgDescriptions);

    // Specify USAGE context
    arg_desc->SetUsageContext(GetArguments().GetProgramBasename(),
                              "Basic sample demo program");
    // Setup arg.descriptions for this application
    SetupArgDescriptions(arg_desc.release());
}


/////////////////////////////////////////////////////////////////////////////
//  Run test (printout arguments obtained from command-line)

int CSampleBasicApplication::Run(void)
{
    cout << "NCBI C++ Toolkit ready" << endl;
    return 0;
}


/////////////////////////////////////////////////////////////////////////////
//  Cleanup

void CSampleBasicApplication::Exit(void)
{
    // Do your after-Run() cleanup here
}


/////////////////////////////////////////////////////////////////////////////
//  MAIN

int NcbiSys_main(int argc, ncbi::TXChar* argv[])
{
    // Execute main application function; change argument list to
    // (argc, argv, 0, eDS_Default, 0) if there's no point in trying
    // to look for an application-specific configuration file.
    return CSampleBasicApplication().AppMain(argc, argv);
}
