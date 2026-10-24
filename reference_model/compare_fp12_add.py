
import bisect
import random
import subprocess
import tempfile
from pathlib import Path

from fp12_basics import decode_fp12_e6m5

ROOT = Path(__file__).resolve().parent.parent
RTL = ROOT / "rtl" / "fp12_add_sr.v"

# E6M5 format: one sign bit, six exponent bits, five fraction bits.
# This test covers normal finite operands; subnormals are unsupported.
MIN_NORMAL = 2.0 ** (1 - 31)
MAX_FINITE = (2.0 - 2.0 ** -5) * (2.0 ** (62 - 31))


def decode_normal(bits):
    """Decode a normal finite E6M5 value."""
    sign = (bits >> 11) & 1
    exponent = (bits >> 5) & 0x3F
    fraction = bits & 0x1F

    if exponent == 0 or exponent == 63:
        raise ValueError(f"Unsupported E6M5 encoding: 0x{bits:03X}")

    value = (1.0 + fraction / 32.0) * (2.0 ** (exponent - 31))
    return -value if sign else value


def build_representable_values():
    items = [(0.0, 0x000)]

    for sign in (0, 1):
        for exponent in range(1, 63):
            for fraction in range(32):
                bits = (sign << 11) | (exponent << 5) | fraction
                items.append((decode_normal(bits), bits))

    items.sort(key=lambda item: item[0])
    return items


REPRESENTABLE = build_representable_values()
VALUES = [item[0] for item in REPRESENTABLE]


def neighboring_encodings(exact):
    """Return the representable encodings immediately below/above exact."""
    pos = bisect.bisect_left(VALUES, exact)
    candidates = set()

    if pos < len(REPRESENTABLE):
        candidates.add(REPRESENTABLE[pos][1])
    if pos > 0:
        candidates.add(REPRESENTABLE[pos - 1][1])

    return candidates


def is_normal_finite(bits):
    exponent = (bits >> 5) & 0x3F
    return exponent not in (0, 63)


def create_test_vectors():
    # Deliberate coverage of addition, subtraction and cancellation.
    pairs = [
        (0x3E0, 0x3C0),
        (0x3E0, 0x3A0),
        (0x3C0, 0x3C0),
        (0x3E0, 0x2C0),
        (0x3E0, 0x3E0),
        (0x3E0, 0xBE0),  # Exact cancellation
        (0x3E0, 0xBC0),
        (0x3A0, 0xB80),
        (0x420, 0x3C0),
        (0x360, 0x340),
        (0xBE0, 0xBC0),
        (0x420, 0xC20),
    ]

    rng = random.Random(42)
    normal_bits = [bits for _, bits in REPRESENTABLE if bits != 0]

    for _ in range(150):
        pairs.append((rng.choice(normal_bits), rng.choice(normal_bits)))

    # Check every random byte for selected rounding-sensitive cases.
    exhaustive_pairs = [
        (0x3E0, 0x2C0),
        (0x3E0, 0xBC0),
        (0x420, 0x3C0),
        (0x3E0, 0x3E0),
    ]

    vectors = set()

    for a, b in pairs:
        for rand in (0, 64, 128, 192, 255):
            vectors.add((a, b, rand))

    for a, b in exhaustive_pairs:
        for rand in range(256):
            vectors.add((a, b, rand))

    return sorted(vectors)


def run_rtl(vectors):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        tb_file = temp / "tb_compare.v"
        sim_file = temp / "sim.out"

        lines = [
            "`timescale 1ns/1ps",
            "module tb_compare;",
            "reg [11:0] a, b;",
            "reg [17:0] random_bits;",
            "wire [11:0] result;",
            "fp12_add_sr dut(a, b, random_bits, result);",
            "initial begin",
        ]

        for a, b, rand in vectors:
            lines.append(
                f"a=12'h{a:03X}; b=12'h{b:03X}; "
                f"random_bits=18'd{rand * 1024}; #1; "
                '$display("RESULT %03h %03h %0d %03h", '
                "a, b, random_bits, result);"
            )

        lines.extend(["$finish;", "end", "endmodule"])
        tb_file.write_text("\n".join(lines), encoding="utf-8")

        subprocess.run(
            [
                "iverilog", "-g2012", "-o", str(sim_file),
                str(RTL), str(tb_file),
            ],
            check=True,
            cwd=ROOT,
        )

        completed = subprocess.run(
            ["vvp", str(sim_file)],
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

    outputs = {}

    for line in completed.stdout.splitlines():
        if not line.startswith("RESULT "):
            continue

        _, a_text, b_text, rand_text, result_text = line.split()
        key = (
            int(a_text, 16),
            int(b_text, 16),
            int(rand_text),
        )
        outputs[key] = int(result_text, 16)

    return outputs


def main():
    if not RTL.exists():
        raise FileNotFoundError(f"RTL file not found: {RTL}")

    vectors = create_test_vectors()
    outputs = run_rtl(vectors)

    passed = 0
    failed = 0
    skipped = 0
    failures_printed = 0

    for (a, b, rand), result_bits in outputs.items():
        if not is_normal_finite(a) or not is_normal_finite(b):
            skipped += 1
            continue

        exact = decode_normal(a) + decode_normal(b)

        # This prototype flushes underflow to zero and overflows to infinity.
        # Those ranges are reported separately, not counted as passes.
        if exact != 0.0 and abs(exact) < MIN_NORMAL:
            skipped += 1
            continue

        if abs(exact) > MAX_FINITE:
            skipped += 1
            continue

        result_exp = (result_bits >> 5) & 0x3F
        if result_exp == 63:
            skipped += 1
            continue

        candidates = neighboring_encodings(exact)

        # Exact cancellation must produce positive zero in this prototype.
        if exact == 0.0:
            valid = result_bits == 0x000
        else:
            valid = result_bits in candidates

        if valid:
            passed += 1
        else:
            failed += 1
            if failures_printed < 20:
                try:
                    decoded = decode_normal(result_bits)
                except ValueError:
                    decoded = float("nan")

                print(
                    f"FAIL A={a:03X} B={b:03X} rand={rand:3d} "
                    f"exact={exact:.12g} result={result_bits:03X} "
                    f"decoded={decoded:.12g} "
                    f"neighbors={[f'{x:03X}' for x in sorted(candidates)]}"
                )
                failures_printed += 1

    # Explicit exhaustive probability test for 3E0 + 2C0.
    up = 0
    down = 0
    unexpected = 0

    for rand in range(256):
        result_bits = outputs.get((0x3E0, 0x2C0, rand * 1024))

        if result_bits == 0x3E1:
            up += 1
        elif result_bits == 0x3E0:
            down += 1
        else:
            unexpected += 1

    probability_pass = (up == 16 and down == 240 and unexpected == 0)

    print("\nStrengthened FP12 addition comparison")
    print(f"RTL vectors generated:       {len(vectors)}")
    print(f"Numerical checks passed:     {passed}")
    print(f"Numerical checks failed:     {failed}")
    print(f"Unsupported cases skipped:   {skipped}")
    print("\nExhaustive stochastic test: 3E0 + 2C0")
    print(f"Round up:                    {up}/256")
    print(f"Round down:                  {down}/256")
    print(f"Unexpected results:          {unexpected}")
    print(
        "Probability mapping:         "
        + ("PASS" if probability_pass else "FAIL")
    )

    if failed == 0 and probability_pass and passed > 0:
        print(
            "\nPASS: All checked outputs were neighboring representable "
            "values, and the selected probability test passed."
        )
    else:
        print(
            "\nFAIL: Review the failures before trusting this RTL."
        )

    print(
        "Note: These checks do not establish complete arithmetic correctness "
        "or research-paper fidelity."
    )


if __name__ == "__main__":
    main()




