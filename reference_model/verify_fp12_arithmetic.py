from fractions import Fraction
import random
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RTL = ROOT / "rtl" / "fp12_add_sr.v"
MIN_NORMAL = Fraction(1, 2**30)
RANDOM_WIDTH = 18
RANDOM_LIMIT = 1 << RANDOM_WIDTH


def decode(bits):
    bits &= 0xFFF
    sign = (bits >> 11) & 1
    exponent = (bits >> 5) & 0x3F
    fraction = bits & 0x1F

    if exponent == 0 or exponent == 63:
        raise ValueError(f"Unsupported encoding: {bits:03X}")

    value = Fraction(32 + fraction, 32)
    power = exponent - 31
    value *= 2**power if power >= 0 else Fraction(1, 2**(-power))
    return -value if sign else value


def build_representable():
    items = [(Fraction(0), 0x000)]
    for sign in (0, 1):
        for exponent in range(1, 63):
            for fraction in range(32):
                bits = (sign << 11) | (exponent << 5) | fraction
                items.append((decode(bits), bits))
    items.sort(key=lambda item: item[0])
    return items


REPRESENTABLE = build_representable()


def neighboring_encodings(exact):
    below = above = None
    for value, bits in REPRESENTABLE:
        if value <= exact:
            below = (value, bits)
        if value >= exact:
            above = (value, bits)
            break

    candidates = set()
    if below is not None:
        candidates.add(below[1])
    if above is not None:
        candidates.add(above[1])
    return candidates


def create_vectors():
    pairs = [
        (0x3E0, 0x3C0),
        (0x3E0, 0x3A0),
        (0x3C0, 0x3C0),
        (0x3E0, 0x2C0),
        (0x3E0, 0x3E0),
        (0x3E0, 0xBE0),
        (0x3E0, 0xBC0),
        (0x3A0, 0xB80),
        (0x420, 0x3C0),
        (0x360, 0x340),
        (0x088, 0x88A),
        (0x088, 0x08A),
        (0x088, 0x88C),
    ]

    rng = random.Random(2026)
    normal = [
        (sign << 11) | (exp << 5) | frac
        for sign in (0, 1)
        for exp in range(1, 63)
        for frac in range(32)
    ]

    for _ in range(200):
        pairs.append((rng.choice(normal), rng.choice(normal)))

    vectors = set()

    # Broadly sample the complete 18-bit random-number range.
    sample_bytes = (0, 64, 128, 192, 255)
    for a, b in pairs:
        for sample in sample_bytes:
            vectors.add((a, b, sample * 1024))

    # Test the threshold boundary using evenly spaced 18-bit samples.
    for a, b in (
        (0x3E0, 0x2C0),
        (0x3E0, 0xBC0),
        (0x420, 0x3C0),
        (0x088, 0x88A),
    ):
        for sample in range(256):
            vectors.add((a, b, sample * 1024))

    return sorted(vectors)


def run_rtl(vectors):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        tb_file = temp / "tb.v"
        exe_file = temp / "sim.out"

        lines = [
            "`timescale 1ns/1ps",
            "module tb;",
            "reg [11:0] a, b;",
            "reg [17:0] random_bits;",
            "wire [11:0] result;",
            "fp12_add_sr dut(a, b, random_bits, result);",
            "initial begin",
        ]

        for a, b, rand in vectors:
            lines.append(
                f"a=12'h{a:03X}; b=12'h{b:03X}; "
                f"random_bits=18'd{rand}; #1; "
                '$display("RESULT %03h %03h %0d %03h", '
                "a,b,random_bits,result);"
            )

        lines.extend(["$finish;", "end", "endmodule"])
        tb_file.write_text("\n".join(lines), encoding="utf-8")

        subprocess.run(
            ["iverilog", "-g2012", "-o", str(exe_file),
             str(RTL), str(tb_file)],
            cwd=ROOT,
            check=True,
        )
        completed = subprocess.run(
            ["vvp", str(exe_file)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )

    outputs = {}
    for line in completed.stdout.splitlines():
        if line.startswith("RESULT "):
            _, a, b, rand, result = line.split()
            outputs[(int(a, 16), int(b, 16), int(rand))] = int(result, 16)
    return outputs


def main():
    if not RTL.exists():
        raise FileNotFoundError(f"RTL not found: {RTL}")

    vectors = create_vectors()
    outputs = run_rtl(vectors)

    passed = failed = skipped = shown = 0

    for (a, b, rand), result in outputs.items():
        exact = decode(a) + decode(b)

        if exact == 0 or abs(exact) < MIN_NORMAL:
            valid = result == 0
        else:
            result_exp = (result >> 5) & 0x3F
            if result_exp == 63:
                skipped += 1
                continue
            valid = (
                result_exp != 0
                and result in neighboring_encodings(exact)
            )

        if valid:
            passed += 1
        else:
            failed += 1
            if shown < 30:
                print(
                    f"FAIL A={a:03X} B={b:03X} rand={rand:6d} "
                    f"exact={float(exact):.12g} result={result:03X}"
                )
                shown += 1

    up = down = unexpected = 0
    for sample in range(256):
        result = outputs[(0x3E0, 0x2C0, sample * 1024)]
        if result == 0x3E1:
            up += 1
        elif result == 0x3E0:
            down += 1
        else:
            unexpected += 1

    probability_pass = up == 16 and down == 240 and unexpected == 0
    regression_pass = all(
        outputs[(0x088, 0x88A, sample * 1024)] == 0
        for sample in range(256)
    )

    print("\nExact-rational arithmetic verification")
    print(f"Random width:                  {RANDOM_WIDTH} bits")
    print(f"Vectors generated:             {len(vectors)}")
    print(f"Passed:                        {passed}")
    print(f"Failed:                        {failed}")
    print(f"Overflow cases skipped:        {skipped}")
    print(f"Probability mapping:           {'PASS' if probability_pass else 'FAIL'}")
    print(f"Underflow regression:          {'PASS' if regression_pass else 'FAIL'}")

    if failed == 0 and probability_pass and regression_pass:
        print("PASS: All checks in this test suite passed.")
    else:
        print("FAIL: Investigate the reported cases.")


if __name__ == "__main__":
    main()