program test_package
  implicit none
  integer :: iam, nprocs, ictxt
  integer :: nprow, npcol, myrow, mycol
  integer :: local_n
  integer :: numroc

  call blacs_pinfo(iam, nprocs)
  call blacs_get(-1, 0, ictxt)

  nprow = 1
  npcol = 1
  call blacs_gridinit(ictxt, 'R', nprow, npcol)
  call blacs_gridinfo(ictxt, nprow, npcol, myrow, mycol)

  local_n = numroc(8, 2, myrow, 0, nprow)
  if (local_n /= 8) stop 1
  if (myrow /= 0 .or. mycol /= 0) stop 2

  call blacs_gridexit(ictxt)
  call blacs_exit(0)

  print *, 'netlib-scalapack test_package OK'
end program test_package
