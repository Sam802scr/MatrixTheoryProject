#!/usr/bin/env bash
# Removes the superseded prototype files (they define clashing module names or have the wrong semantics).
# Review the list, then run from the repo root:  bash cleanup_old_files.sh
git rm -r --cached --ignore-unmatch __pycache__ reference_model/__pycache__ >/dev/null 2>&1
git rm -f --ignore-unmatch \
  rtl/fp12_add_sr.v rtl/fp12_add_sr_eager_draft.v rtl/mac.v rtl/adder.v rtl/fp12_accumulator.v \
  rtl/sr_rounding_unit.v rtl/stochastic_round.v rtl/lfsr.v \
  testbench/tb_fp12_sticky_round.v testbench/tb_fp12_round_correction.v testbench/tb_fp12_add_sr.v testbench/tb_fp12_add_sr.out testbench/tb_adder.v testbench/tb_mac.v testbench/tb_lfsr.v testbench/tb_fp12_accumulator.v testbench/tb_sr_rounding_unit.v testbench/tb_stochastic_round.v \
  sim.out sticky_check eager_test
echo "done. Old reference_model/*.py scripts are kept; sr_mac_ref.py supersedes them."
