#!/usr/bin/env bash
# Open-source ASIC proxy: Yosys + ABC mapped to the Nangate 45nm typical-corner library. Area in um^2, delay in ps (post-mapping, no wire load).
# NOT the paper's Synopsys / 28nm FDSOI flow -> compare RATIOS (eager vs lazy vs RN), not absolute numbers.   Run on Linux/WSL/macOS with yosys installed.
cd "$(dirname "$0")/.."
LIB=synth/NangateOpenCellLibrary_typical.lib
[ -f $LIB ] || curl -sL -o $LIB https://raw.githubusercontent.com/The-OpenROAD-Project/OpenROAD-flow-scripts/master/flow/platforms/nangate45/lib/NangateOpenCellLibrary_typical.lib
OUT=results/hardware_proxy.csv; echo "design,r,area_um2,delay_ps,cells" > $OUT
run() { # name top files R
  local P=""; [ -n "$4" ] && P="chparam -set R $4 $2;"
  local LOG=$(yosys -p "read_verilog $3; $P synth -top $2 -flatten; abc -liberty $LIB -script +strash;dch;map;topo;stime,-p;buffer,-c;upsize,-c;dnsize,-c;stime,-p; stat -liberty $LIB" 2>&1)
  local D=$(echo "$LOG" | grep "Delay =" | tail -1 | sed 's/.*Delay = *\([0-9.]*\) ps.*/\1/')
  local A=$(echo "$LOG" | grep "Chip area" | tail -1 | awk '{print $NF}')
  local C=$(echo "$LOG" | grep "Gates =" | tail -1 | sed 's/.*Gates = *\([0-9]*\).*/\1/')
  echo "$1,${4:--},$A,$D,$C" | tee -a $OUT
}
EAG="rtl/fp12_sticky_round.v rtl/fp12_round_correction.v rtl/fp12_add_sr_eager.v"
run RN_E6M5           fp12_add           rtl/fp12_add.v ""
for R in 9 12 14 16 18; do run SR_eager_E6M5 fp12_add_sr_eager "$EAG" $R; done
for R in 9 18;          do run SR_lazy_E6M5  fp12_add_sr_lazy  rtl/fp12_add_sr_lazy.v $R; done
