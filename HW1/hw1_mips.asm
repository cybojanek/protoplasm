##############################################################################
# Input: n                                                                   #
# Output: max(k) for 2^k such that n! is divisble by 2^k                     #
# Algorithm: sum of n/2 + n/4 + n/8 + ... + n/2^31                           #
# Collect all twos from prime factorization of n, n-1, ..., 1                #
# Runtime: O(1)                                                              #
##############################################################################
.data

.text
main:
li $v0, 5			# Read integer n
syscall

li $a0, 1			# -1 return value if n is <= 0
blez $v0, exit		# check if n is <= 0, is so then exit

move $t0, $v0		# Move integer n to t0
li $t1, 0			# Set exponent k to 0
li $t2, 0			# Set shift to 0

for:
sra $t0, $t0, 1		# Divide by 2
add $t1, $t1, $t0	# Add to k
addi $t2, $t2, 1	# Count how many times we've shifted
beq $t2, 31, end	# Stop if we've shifted 31 times
j for				# Go again

end:
li $v0, 1			# Print integer
move $a0, $t1
syscall

li $a0, 0			# All is good

exit:
li $v0, 17			# Exit with value
syscall
