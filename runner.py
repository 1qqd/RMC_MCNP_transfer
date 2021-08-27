# -*- coding:utf-8 -*-
# author: Shen PF
# date: 2021-07-23
"""
examples:
>>> inp_MCNP = '06'
>>> M2R.transfer(inp_MCNP)
"""


import MCNPtoRMC as M2R
import os
import re


print("Hello! Start with the MCNP to RMC transformation tools! \nAuthor: ShenPF")

# files = ['0'+str(i+1) for i in range(8)]
# for file in files:
#     M2R.transfer(file)

filename = input("\nPlease input the filename: \nnote: '*' and '?' can be used. \n")
print("You have input : " + filename + '\n')
reg = filename.replace('?', '.')
reg = reg.replace('*', '.*')

processed_files = []
path = os.getcwd()
for file in os.listdir(path):
    if re.match(r'^'+reg+'$', file) and len(file) >= len(reg)-1:
        processed_files.append(file)

for file in processed_files:
    M2R.transfer(file)
