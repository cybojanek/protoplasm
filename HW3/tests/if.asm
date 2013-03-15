.text
main:
li $t1, 0                     # a = 0
li $t3, 1                     # b = 1
li $t2, 2                     # c = 2
beqz $t1, l_22_end_if         # if a then...
move $a0, $t1                 # print(a)
li $v0, 1                     # 
syscall                       # 
li $a0, 10                    # newline
li $v0, 11                    # 
syscall                       # 
l_22_end_if:                  # 
beqz $t1, l_24_else           # if a then...else...
move $a0, $t1                 # print(a)
li $v0, 1                     # 
syscall                       # 
li $a0, 10                    # newline
li $v0, 11                    # 
syscall                       # 
b l_23_end_if                 # 
l_24_else:                    # 
move $a0, $t3                 # print(b)
li $v0, 1                     # 
syscall                       # 
li $a0, 10                    # newline
li $v0, 11                    # 
syscall                       # 
l_23_end_if:                  # 
beqz $t3, l_25_end_if         # if b then...
move $a0, $t3                 # print(b)
li $v0, 1                     # 
syscall                       # 
li $a0, 10                    # newline
li $v0, 11                    # 
syscall                       # 
l_25_end_if:                  # 
beqz $t3, l_27_else           # if b then...else...
move $a0, $t3                 # print(b)
li $v0, 1                     # 
syscall                       # 
li $a0, 10                    # newline
li $v0, 11                    # 
syscall                       # 
b l_26_end_if                 # 
l_27_else:                    # 
move $a0, $t2                 # print(c)
li $v0, 1                     # 
syscall                       # 
li $a0, 10                    # newline
li $v0, 11                    # 
syscall                       # 
l_26_end_if:                  # 
beqz $t1, l_28_end_if         # if a then...
beqz $t3, l_29_end_if         # if b then...
move $a0, $t3                 # print(b)
li $v0, 1                     # 
syscall                       # 
li $a0, 10                    # newline
li $v0, 11                    # 
syscall                       # 
l_29_end_if:                  # 
l_28_end_if:                  # 
beqz $t3, l_30_end_if         # if b then...
beqz $t2, l_31_end_if         # if c then...
move $a0, $t2                 # print(c)
li $v0, 1                     # 
syscall                       # 
li $a0, 10                    # newline
li $v0, 11                    # 
syscall                       # 
l_31_end_if:                  # 
l_30_end_if:                  # 
beqz $t3, l_33_else           # if b then...else...
beqz $t2, l_35_else           # if c then...else...
move $a0, $t2                 # print(c)
li $v0, 1                     # 
syscall                       # 
li $a0, 10                    # newline
li $v0, 11                    # 
syscall                       # 
b l_34_end_if                 # 
l_35_else:                    # 
move $a0, $t3                 # print(b)
li $v0, 1                     # 
syscall                       # 
li $a0, 10                    # newline
li $v0, 11                    # 
syscall                       # 
l_34_end_if:                  # 
b l_32_end_if                 # 
l_33_else:                    # 
move $a0, $t1                 # print(a)
li $v0, 1                     # 
syscall                       # 
li $a0, 10                    # newline
li $v0, 11                    # 
syscall                       # 
l_32_end_if:                  # 
beqz $t1, l_37_else           # if a then...else...
beqz $t2, l_39_else           # if c then...else...
move $a0, $t2                 # print(c)
li $v0, 1                     # 
syscall                       # 
li $a0, 10                    # newline
li $v0, 11                    # 
syscall                       # 
b l_38_end_if                 # 
l_39_else:                    # 
move $a0, $t3                 # print(b)
li $v0, 1                     # 
syscall                       # 
li $a0, 10                    # newline
li $v0, 11                    # 
syscall                       # 
l_38_end_if:                  # 
b l_36_end_if                 # 
l_37_else:                    # 
move $a0, $t1                 # print(a)
li $v0, 1                     # 
syscall                       # 
li $a0, 10                    # newline
li $v0, 11                    # 
syscall                       # 
l_36_end_if:                  # 
seq $t9, $t1, 0               # @0 = ! a
beqz $t9, l_40_end_if         # if @0 then...
move $a0, $t3                 # print(b)
li $v0, 1                     # 
syscall                       # 
li $a0, 10                    # newline
li $v0, 11                    # 
syscall                       # 
l_40_end_if:                  # 
bnez $t1, l_41_use_arg1       # @1 = a || b
move $t9, $t3                 # 
b l_42_done                   # 
l_41_use_arg1:                # 
move $t9, $t1                 # 
l_42_done:                    # 
beqz $t9, l_43_end_if         # if @1 then...
move $a0, $t3                 # print(b)
li $v0, 1                     # 
syscall                       # 
li $a0, 10                    # newline
li $v0, 11                    # 
syscall                       # 
l_43_end_if:                  # 
beqz $t3, l_44_set_0          # @2 = b && c
move $t9, $t2                 # 
b l_45_done                   # 
l_44_set_0:                   # 
li $t9, 0                     # 
l_45_done:                    # 
beqz $t9, l_46_end_if         # if @2 then...
move $a0, $t3                 # print(b)
li $v0, 1                     # 
syscall                       # 
li $a0, 10                    # newline
li $v0, 11                    # 
syscall                       # 
l_46_end_if:                  # 
li $t9, 0                     # @19 = 0
sgt $t8, $t1, $t9             # @3 = a > @19
li $t9, 1                     # @20 = 1
sgt $t9, $t3, $t9             # @4 = b > @20
bnez $t8, l_47_use_arg1       # @5 = @3 || @4
move $t9, $t9                 # 
b l_48_done                   # 
l_47_use_arg1:                # 
move $t9, $t8                 # 
l_48_done:                    # 
li $t8, 2                     # @21 = 2
sgt $t8, $t2, $t8             # @6 = c > @21
bnez $t9, l_49_use_arg1       # @7 = @5 || @6
move $t9, $t8                 # 
b l_50_done                   # 
l_49_use_arg1:                # 
move $t9, $t9                 # 
l_50_done:                    # 
beqz $t9, l_51_end_if         # if @7 then...
move $a0, $t2                 # print(c)
li $v0, 1                     # 
syscall                       # 
li $a0, 10                    # newline
li $v0, 11                    # 
syscall                       # 
l_51_end_if:                  # 
beqz $t2, l_53_else           # if c then...else...
li $t9, 1                     # d = 1
b l_52_end_if                 # 
l_53_else:                    # 
li $t9, 0                     # d = 0
l_52_end_if:                  # 
beqz $t9, l_54_end_if         # if d then...
move $a0, $t9                 # print(d)
li $v0, 1                     # 
syscall                       # 
li $a0, 10                    # newline
li $v0, 11                    # 
syscall                       # 
l_54_end_if:                  # 
beqz $t1, l_55_set_0          # @8 = a && b
move $t9, $t3                 # 
b l_56_done                   # 
l_55_set_0:                   # 
li $t9, 0                     # 
l_56_done:                    # 
seq $t9, $t9, 0               # @9 = ! @8
seq $t0, $t1, 0               # @10 = ! a
seq $t8, $t3, 0               # @11 = ! b
bnez $t0, l_57_use_arg1       # @12 = @10 || @11
move $t8, $t8                 # 
b l_58_done                   # 
l_57_use_arg1:                # 
move $t8, $t0                 # 
l_58_done:                    # 
seq $t9, $t9, $t8             # @13 = @9 == @12
beqz $t9, l_59_end_if         # if @13 then...
move $a0, $t2                 # print(c)
li $v0, 1                     # 
syscall                       # 
li $a0, 10                    # newline
li $v0, 11                    # 
syscall                       # 
l_59_end_if:                  # 
beqz $t1, l_60_set_0          # @14 = a && b
move $t0, $t3                 # 
b l_61_done                   # 
l_60_set_0:                   # 
li $t0, 0                     # 
l_61_done:                    # 
seq $t8, $t1, 0               # @15 = ! a
seq $t9, $t3, 0               # @16 = ! b
bnez $t8, l_62_use_arg1       # @17 = @15 || @16
move $t9, $t9                 # 
b l_63_done                   # 
l_62_use_arg1:                # 
move $t9, $t8                 # 
l_63_done:                    # 
sne $t9, $t0, $t9             # @18 = @14 != @17
beqz $t9, l_64_end_if         # if @18 then...
move $a0, $t2                 # print(c)
li $v0, 1                     # 
syscall                       # 
li $a0, 10                    # newline
li $v0, 11                    # 
syscall                       # 
l_64_end_if:                  # 
# Exit gracefully
li $v0, 10
syscall
