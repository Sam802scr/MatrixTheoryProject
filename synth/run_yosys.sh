#!/usr/bin/env bash
# Exploratory area proxy (NOT the paper's 28nm FDSOI / Vivado numbers): generic-gate cell count and Xilinx LUT count.
cd "$(dirname "$0")/.."
for top in fp12_add fp12_add_sr_lazy fp12_add_sr_eager; do
  F="rtl/$top.v"
  [ "$top" = fp12_add_sr_eager ] && F="rtl/fp12_sticky_round.v rtl/fp12_round_correction.v rtl/fp12_add_sr_eager.v"
  G=$(yosys -q -p "read_verilog $F; synth -top $top -flatten; abc -g AND,NAND,OR,NOR,XOR,XNOR,MUX; tee -o /dev/stdout stat" 2>&1 | awk '/Number of cells/{print $4; exit}')
  L=$(yosys -q -p "read_verilog $F; synth_xilinx -top $top -flatten; tee -o /dev/stdout stat" 2>&1 | awk '/LUT[1-6] /{s+=$2} END{print s}')
  printf "%-20s generic gates: %5s   Xilinx LUTs: %4s\n" "$top" "$G" "$L"
done
