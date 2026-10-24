
from fp12_alignment import (
    align_fp12,
    align_fp12_extended,
    encode_normal_fp12,
)

# Two exactly representable E6M5 values
a_bits = encode_normal_fp12(1.0)
b_bits = encode_normal_fp12(0.15625)

basic = align_fp12(a_bits, b_bits)
extended = align_fp12_extended(a_bits, b_bits, extra_bits=3)

print("Basic alignment")
print("Aligned significands:", basic[1], basic[3])
print("Common exponent:", basic[4])

print("\nExtended alignment")
print("Aligned significands:", extended[1], extended[3])
print("Common exponent:", extended[4])
print("Extra bits:", extended[5])

# Check what the right shift discards
_, exp_b, sig_b = __import__(
    "fp12_alignment"
).get_fp12_fields(b_bits)

shift_b = extended[4] - exp_b
shifted_before_alignment = sig_b << extended[5]
discarded_bits = shifted_before_alignment & ((1 << shift_b) - 1)

print("Shift amount:", shift_b)
print("Bits before alignment:", bin(shifted_before_alignment))
print("Aligned result:", shifted_before_alignment >> shift_b)
print("Discarded bits:", bin(discarded_bits))
print("Any discarded 1-bits:", discarded_bits != 0)

# print("\nDiscarded-bit check")
# print("Shift amount:", shift_b)
# print("Bits before alignment:", bin(shifted_before_alignment))
# print("Discarded bits:", bin(discarded_bits))

print("\nDirect discarded-bit test")

test_value = 0b101001011
test_shift = 3

aligned = test_value >> test_shift
discarded = test_value & ((1 << test_shift) - 1)
sticky = discarded != 0

print("Original bits:", bin(test_value))
print("Shift amount:", test_shift)
print("Aligned result:", bin(aligned))
print("Discarded bits:", bin(discarded))
print("Sticky bit:", int(sticky))

print("\nUpdated helper output")

print("Discarded bits for A:", extended[6])
print("Discarded bits for B:", extended[7])
print("Sticky bit for A:", extended[8])
print("Sticky bit for B:", extended[9])

print("\nControlled discarded-bit test")

test_sig = 0b101001011
test_shift = 3

discarded = test_sig & ((1 << test_shift) - 1)
sticky = int(discarded != 0)

print("Original significand:", bin(test_sig))
print("Discarded bits:", bin(discarded))
print("Sticky bit:", sticky)