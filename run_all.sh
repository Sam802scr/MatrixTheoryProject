#!/usr/bin/env bash
# One command: golden-model tests -> vector generation -> RTL simulation. Run from the repo root.
set -e
RTL="rtl/fp8_multiplier.v rtl/lfsr_galois.v rtl/fp12_add.v rtl/fp12_add_sr_lazy.v rtl/fp12_sticky_round.v rtl/fp12_round_correction.v rtl/fp12_add_sr_eager.v rtl/fp_mac.v"
mkdir -p build
(cd reference_model && python3 test_sr_mac.py && python3 gen_vectors.py)
iverilog -g2012 -o build/tb_vectors     $RTL testbench/tb_vectors.v
iverilog -g2012 -o build/tb_mac_vectors $RTL testbench/tb_mac_vectors.v
vvp build/tb_vectors     | grep -v finish
vvp build/tb_mac_vectors | grep -v finish
