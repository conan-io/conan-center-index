
program example
  use COLLIER
  implicit none

  character(len=5) :: version

  call GetVersionNumber_cll(version)

  write(*, *) "COLLIER (version ", version, ")"

end program example
