
from fp8_basics import decode_fp8_e5m2
from fp12_accumulator import accumulate_fp12
from fp12_basics import decode_fp12_e6m5
from fp12_alignment import encode_normal_fp12


def mac_step(acc_bits, a_bits, b_bits, mode="nearest"):
    """
    One MAC step:
    1. Decode FP8 inputs.
    2. Multiply them.
    3. Add the product to the FP12 accumulator.
    4. Round the accumulator result.
    """
    a = decode_fp8_e5m2(a_bits)
    b = decode_fp8_e5m2(b_bits)

    product = a * b

    new_acc_bits = accumulate_fp12(
        acc_bits, product, mode=mode
    )

    return new_acc_bits


def run_mac(a_bits_list, b_bits_list, mode="nearest"):
    """Run a sequence of MAC operations."""
    if len(a_bits_list) != len(b_bits_list):
        raise ValueError("Input lists must have equal lengths.")

    acc_bits = encode_normal_fp12(1.0)

    for a_bits, b_bits in zip(a_bits_list, b_bits_list):
        acc_bits = mac_step(
            acc_bits, a_bits, b_bits, mode=mode
        )

    return acc_bits


if __name__ == "__main__":
    # FP8 E5M2: 1.0 = 00111100
    one = 0b00111100

    # FP8 E5M2: 0.5 = 00111000
    half = 0b00111000

    initial_acc = encode_normal_fp12(1.0)

    result_bits = mac_step(
        initial_acc, one, half, mode="nearest"
    )

    print("Initial accumulator:",
          decode_fp12_e6m5(initial_acc))
    print("Product:",
          decode_fp8_e5m2(one) * decode_fp8_e5m2(half))
    print("Final accumulator:",
          decode_fp12_e6m5(result_bits))
