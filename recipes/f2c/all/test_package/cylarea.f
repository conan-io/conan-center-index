      SUBROUTINE CYLAREA( R, H, V )
      REAL R, H, V
      REAL PI

      PARAMETER ( PI = 3.141592653589793 )

      PRINT*,"arguments of cylarea are ", R, " and ", H

      V = 2 * PI * R * (R + H)

      PRINT*,"I will return ", V

      RETURN

      END
