.text
main:
li $t8, 0                     # x = 0
l_23_while:                   # 
li $t9, 10                    # @12 = 10
sne $t9, $t8, $t9             # @0 = x != @12
beqz $t9, l_28_end_while      # while @0 do...
li $t9, 1                     # @13 = 1
add $t9, $t8, $t9             # @1 = x + @13
move $t8, $t9                 # x = @1
b l_23_while                  # 
l_28_end_while:               # 
move $a0, $t8                 # print(x)
li $v0, 1                     # 
syscall                       # 
li $a0, 10                    # newline
li $v0, 11                    # 
syscall                       # 
li $t8, 0                     # x = 0
l_24_while:                   # 
li $t9, 10                    # @14 = 10
slt $t9, $t8, $t9             # @2 = x < @14
beqz $t9, l_29_end_while      # while @2 do...
li $t9, 1                     # @15 = 1
add $t9, $t8, $t9             # @3 = x + @15
move $t8, $t9                 # x = @3
b l_24_while                  # 
l_29_end_while:               # 
move $a0, $t8                 # print(x)
li $v0, 1                     # 
syscall                       # 
li $a0, 10                    # newline
li $v0, 11                    # 
syscall                       # 
li $t8, 0                     # x = 0
l_25_while:                   # 
li $t9, 10                    # @16 = 10
sle $t9, $t8, $t9             # @4 = x <= @16
beqz $t9, l_30_end_while      # while @4 do...
li $t9, 1                     # @17 = 1
add $t9, $t8, $t9             # @5 = x + @17
move $t8, $t9                 # x = @5
b l_25_while                  # 
l_30_end_while:               # 
move $a0, $t8                 # print(x)
li $v0, 1                     # 
syscall                       # 
li $a0, 10                    # newline
li $v0, 11                    # 
syscall                       # 
li $t8, 0                     # x = 0
l_26_while:                   # 
li $t9, 20                    # @18 = 20
sle $t9, $t8, $t9             # @6 = x <= @18
beqz $t9, l_31_end_while      # while @6 do...
li $t9, 1                     # @19 = 1
add $t9, $t8, $t9             # @7 = x + @19
move $t8, $t9                 # x = @7
li $t9, 3                     # @20 = 3
rem $t9, $t8, $t9             # @8 = x % @20
li $t3, 0                     # @21 = 0
seq $t9, $t9, $t3             # @9 = @8 == @21
beqz $t9, l_32_end_if         # if @9 then...
move $a0, $t8                 # print(x)
li $v0, 1                     # 
syscall                       # 
li $a0, 10                    # newline
li $v0, 11                    # 
syscall                       # 
l_32_end_if:                  # 
b l_26_while                  # 
l_31_end_while:               # 
li $t3, 0                     # a = 0
li $t8, 1                     # b = 1
l_27_while:                   # 
li $t9, 800                   # @22 = 800
sle $t9, $t8, $t9             # @10 = b <= @22
beqz $t9, l_33_end_while      # while @10 do...
add $t9, $t8, $t3             # @11 = b + a
move $t9, $t9                 # c = @11
move $t3, $t8                 # a = b
move $t8, $t9                 # b = c
move $a0, $t9                 # print(c)
li $v0, 1                     # 
syscall                       # 
li $a0, 10                    # newline
li $v0, 11                    # 
syscall                       # 
b l_27_while                  # 
l_33_end_while:               # 
# Exit gracefully
li $v0, 10
syscall
