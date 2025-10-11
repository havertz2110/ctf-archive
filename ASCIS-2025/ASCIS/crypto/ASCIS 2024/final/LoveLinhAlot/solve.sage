from math import prod
from Crypto.Util.number import * 
import os
os.environ['PWNLIB_NOTERM'] = '1'
os.environ['TERM'] = 'xterm-256color'
# os.path.append("/mnt/e/tvdat20004/CTF/tools")
# from solve_ineq import * 
# load("https://raw.githubusercontent.com/TheBlupper/linineq/main/linineq.py")
load('https://gist.githubusercontent.com/Connor-McCartney/952583ecac836f843f50b785c7cb283d/raw/5718ebd8c9b4f9a549746094877a97e7796752eb/solvelinmod.py')

from pwn import * 
io = remote("183.91.11.30", 5000)
# io = process(["python3", "server.py"])
q1 = 57895665874783536962369408363969823887021530656373208299565102620846005563716018275834077962292286213472570266375824572745671541793458387390711613089471407869558363212866932533545785125988453002675479793768261480181947144057144941974626043243654731721303589851520175899531854692118423229594279209070187162279
p1 = 2 * q1 + 1
g1 = 2

BLOCK_LEN = 129
CHARSET = string.ascii_uppercase + string.ascii_lowercase + string.digits

def get_token(username):
	io.sendlineafter(b'> ', b'1337')
	io.sendlineafter(b'Give me the victim name: ', username.encode())	
	io.recvline()
	token = eval(io.recvlineS().strip())
	return token 

def register(username, password, login=False):
	if login:
		io.sendlineafter(b'> ', b'2')
	else:
		io.sendlineafter(b'> ', b'1')
	io.sendlineafter(b'Enter username: ', username.encode())
	io.sendlineafter(b'Enter password: ', password.encode())


password = ''.join(random.choices(CHARSET, k = 128)).encode() + b'\0'
print(password)
register("dat", password.hex())
# io.interactive()
token_admin = get_token("admin")
token = get_token("dat")
# bases_admin = [pow(2, x, p1) for x in token_admin] + [2]
value = sum([x*b for b,x in zip(token, password)]) % q1
v = var(" ".join(f'v{i}' for i in range(128)))
equa = 0
bounds = {}
for i in range(128):
	bounds[v[i]] = 128*100
	equa += v[i] * token_admin[i]

sol = solve_linear_mod([(equa ==value,q1)], bounds)
sol = [int(sol[i]) for i in v]
# print(sol)
assert all(i < 128*100 for i in sol)

newpass = [0]*100*129
print(sum(x*b for x,b in zip(token_admin, sol)) % q1)
print(value)
for j in range(128):
	for i in range(100):
		if sol[j] > 128:
			sol[j] -= 127
			newpass[j + i*129] = 127
		else:
			newpass[j + i*129] = sol[j]
			break
# print(newpass)
newpass = bytes(newpass)

register("aaa", newpass.hex())

register("admin", newpass.hex(), login=True)
io.interactive()
