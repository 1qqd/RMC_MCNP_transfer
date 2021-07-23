# -*- coding:utf-8 -*-
# author: Shen PF
# date: 2021-07-23
"""
examples:
>>> inp_MCNP = '06'
>>> M2R.transfer(inp_MCNP)
"""


import MCNPtoRMC as M2R


print("Hello! Start with the MCNP to RMC transformation tools! \nAuthor: ShenPF")

inp_MCNP = '06'
M2R.transfer(inp_MCNP)

files = ['0'+str(i+1) for i in range(10)]
for file in files:
    M2R.transfer(file)
