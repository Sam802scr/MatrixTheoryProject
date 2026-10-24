
from fp12_accumulator import accumulate_fp12
from fp12_basics import decode_fp12_e6m5
from fp12_alignment import encode_normal_fp12

acc_bits = encode_normal_fp12(1.0)
product = 0.3

nearest_bits = accumulate_fp12(
    acc_bits, product, mode="nearest"
)

stochastic_bits = accumulate_fp12(
    acc_bits, product, mode="stochastic"
)

print("Initial accumulator:", decode_fp12_e6m5(acc_bits))
print("Product:", product)
print("Exact sum:", 1.0 + product)
print(
    "Nearest result:",
    decode_fp12_e6m5(nearest_bits),
)
print(
    "Stochastic result:",
    decode_fp12_e6m5(stochastic_bits),
)
