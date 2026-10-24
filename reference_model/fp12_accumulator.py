
from fp12_basics import decode_fp12_e6m5
from fp12_rounding import round_fp12


def accumulate_fp12(acc_bits, product, mode="nearest"):
    """
    Add a floating-point product to an FP12 accumulator,
    then round the result using the selected mode.
    """
    accumulator = decode_fp12_e6m5(acc_bits)
    exact_sum = accumulator + product

    result_bits = round_fp12(exact_sum, mode=mode)
    return result_bits
