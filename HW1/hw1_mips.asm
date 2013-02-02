##############################################################################
# Input: n                                                                   #
# Output: max(k) for 2^k such that n! is divisble by 2^k                     #
# Algorithm: sum of n/2 + n/4 + n/8 + ... + n/2^31                           #
# Collect all twos from prime factorization of n, n-1, ..., 1                #
# Runtime: O(log_2(n))                                                       #
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
li $t2, 2			# Set current power to 2^1
li $t4, 1			# Max to prevent overflow from next shift
sll $t4, $t4, 30

while:
div $t3, $t0, $t2	# Integer division of n by (2,4,8,16...)
add $t1, $t1, $t3   # k += n / (2,4,8,16...)
bge $t2, $t4, end	# Check that our next shift will not overflow
sll $t2, $t2, 1		# Multiply by 2 for (2,4,8,16...)
bgt $t2, $t0, end	# If the next power is > n, we're done
j while				# Go back if (2,4,8,16...) <= n

end:
li $v0, 1			# Print integer
move $a0, $t1
syscall

li $a0, 0			# All is good

exit:
li $v0, 17			# Exit with value
syscall
