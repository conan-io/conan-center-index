@.str = private unnamed_addr constant [25 x i8] c"LLVM IR interpreter ok!\0A\00", align 1
define i32 @test() #0 {
  call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([25 x i8], [25 x i8]* @.str, i64 0, i64 0))
  ret i32 0
}
declare i32 @printf(i8*, ...) #1
