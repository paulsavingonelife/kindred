@REM////////////////////////////////////////////////////////////////////////////
@REM// File:          run.bat                                                // 
@REM// Project:       Kindred                                                // 
@REM// Author:        Paul Klein                                             // 
@REM// EMail:         pauljkaz@gmail.com                                     // 
@REM// -----                                                                 // 
@REM// Last Modified: Mon Jul 31 2023                                        // 
@REM// Modified By:   Paul Klein                                             // 
@REM// -----                                                                 // 
@REM//                                                                       // 
@REM//  Copyright (c) 2019 - 2023 N/A, All Rights Reserved.                  // 
@REM//                                                                       // 
@REM////////////////////////////////////////////////////////////////////////////

python src/simple/kindredsim.py --workload workloads/%1.s --vcd_trace %1.vcd --inst_trace %1.inst

