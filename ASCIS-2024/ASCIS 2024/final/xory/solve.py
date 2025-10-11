from pwn import xor 
ct = bytes.fromhex('cc76e47d35f67d976639bc10f84355b94ef80500d25c974139e64b974339db6ef2496c')
format = b'ASCIS'
key = xor(format, ct[:5])
print(key)
print(xor(ct, key))


