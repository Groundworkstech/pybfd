
#ifndef __SUPPORTED_DISASM_H_
#define __SUPPORTED_DISASM_H_

#include "bfd_headers.h"

//
// Supported architectures
//
typedef struct _supported_disasm
{
    enum bfd_architecture   bfd_arch;
    disassembler_ftype      bfd_print_insn_endian_little;
    disassembler_ftype      bfd_print_insn_endian_big;
} supported_disasm, *p_supported_disasm;


supported_disasm p_supported_disasm_list[]= {
    {bfd_arch_m68k, print_insn_m68k, print_insn_m68k},
    {bfd_arch_vax, print_insn_vax, print_insn_vax},
    {bfd_arch_i960, print_insn_i960, print_insn_i960},
    {bfd_arch_or32, print_insn_little_or32, print_insn_big_or32},
    {bfd_arch_sparc, print_insn_sparc, print_insn_sparc},
    {bfd_arch_spu, print_insn_spu, print_insn_spu},
    {bfd_arch_mips, print_insn_little_mips, print_insn_big_mips},
    {bfd_arch_i386, print_insn_i386, print_insn_i386},
    {bfd_arch_l1om, print_insn_i386, print_insn_i386},
    {bfd_arch_k1om, print_insn_i386, print_insn_i386},
    {bfd_arch_i860, print_insn_i860, print_insn_i860},
    {bfd_arch_i370, print_insn_i370, print_insn_i370},
    {bfd_arch_m88k, print_insn_m88k, print_insn_m88k},
    {bfd_arch_h8300, print_insn_h8300, print_insn_h8300},
    {bfd_arch_pdp11, print_insn_pdp11, print_insn_pdp11},
    {bfd_arch_powerpc, print_insn_little_powerpc, print_insn_big_powerpc},
    {bfd_arch_rs6000, print_insn_rs6000, print_insn_rs6000},
    {bfd_arch_hppa, print_insn_hppa, print_insn_hppa},
    {bfd_arch_d10v, print_insn_d10v, print_insn_d10v},
    {bfd_arch_d30v, print_insn_d30v, print_insn_d30v},
    {bfd_arch_dlx, print_insn_dlx, print_insn_dlx},
    {bfd_arch_m68hc11, print_insn_m68hc11, print_insn_m68hc11},
    {bfd_arch_z8k, print_insn_z8002, print_insn_z8002},
    {bfd_arch_h8500, print_insn_h8500, print_insn_h8500},
    {bfd_arch_sh, print_insn_sh, print_insn_sh},
    {bfd_arch_alpha, print_insn_alpha, print_insn_alpha},
    {bfd_arch_arm, print_insn_little_arm, print_insn_big_arm},
    {bfd_arch_ns32k, print_insn_ns32k, print_insn_ns32k},
    {bfd_arch_w65, print_insn_w65, print_insn_w65},
    {bfd_arch_tic30, print_insn_tic30, print_insn_tic30},
    {bfd_arch_tic4x, print_insn_tic4x, print_insn_tic4x},
    {bfd_arch_tic54x, print_insn_tic54x, print_insn_tic54x},
    {bfd_arch_tic6x, print_insn_tic6x, print_insn_tic6x},
    {bfd_arch_tic80, print_insn_tic80, print_insn_tic80},
    {bfd_arch_m32c, print_insn_m32c, print_insn_m32c},
    {bfd_arch_m32r, print_insn_m32r, print_insn_m32r},
    {bfd_arch_mn10200, print_insn_mn10200, print_insn_mn10200},
    {bfd_arch_mn10300, print_insn_mn10300, print_insn_mn10300},
    {bfd_arch_fr30, print_insn_fr30, print_insn_fr30},
    {bfd_arch_frv, print_insn_frv, print_insn_frv},
    {bfd_arch_moxie, print_insn_moxie, print_insn_moxie},
    {bfd_arch_mcore, print_insn_mcore, print_insn_mcore},
    {bfd_arch_mep, print_insn_mep, print_insn_mep},
    {bfd_arch_ia64, print_insn_ia64, print_insn_ia64},
    {bfd_arch_iq2000, print_insn_iq2000, print_insn_iq2000},
    {bfd_arch_mt, print_insn_mt, print_insn_mt},
    {bfd_arch_pj, print_insn_pj, print_insn_pj},
    {bfd_arch_avr, print_insn_avr, print_insn_avr},
    {bfd_arch_bfin, print_insn_bfin, print_insn_bfin},
    {bfd_arch_cr16c, print_insn_cr16, print_insn_cr16},
    {bfd_arch_crx, print_insn_crx, print_insn_crx},
    {bfd_arch_rx, print_insn_rx, print_insn_rx},
    {bfd_arch_s390, print_insn_s390, print_insn_s390},
    {bfd_arch_score, print_insn_little_score, print_insn_big_score},
    {bfd_arch_openrisc, print_insn_openrisc, print_insn_openrisc},
    {bfd_arch_mmix, print_insn_mmix, print_insn_mmix},
    {bfd_arch_xstormy16, print_insn_xstormy16, print_insn_xstormy16},
    {bfd_arch_msp430, print_insn_msp430, print_insn_msp430},
    {bfd_arch_xc16x, print_insn_xc16x, print_insn_xc16x},
    {bfd_arch_xtensa, print_insn_xtensa, print_insn_xtensa},
    {bfd_arch_z80, print_insn_z80, print_insn_z80},
    {bfd_arch_lm32, print_insn_lm32, print_insn_lm32},
    {bfd_arch_microblaze, print_insn_microblaze, print_insn_microblaze},
    {bfd_arch_tilepro, print_insn_tilepro, print_insn_tilepro},
    {bfd_arch_tilegx, print_insn_tilegx, print_insn_tilegx},
    {bfd_arch_aarch64, print_insn_aarch64, print_insn_aarch64},
    {bfd_arch_rl78, print_insn_rl78, print_insn_rl78}
};

#endif // __SUPPORTED_DISASM_H_
