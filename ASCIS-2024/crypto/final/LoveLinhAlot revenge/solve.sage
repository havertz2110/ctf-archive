from math import prod
from Crypto.Util.number import * 
import os
os.environ['PWNLIB_NOTERM'] = '1'
os.environ['TERM'] = 'xterm-256color'

load('https://gist.githubusercontent.com/Connor-McCartney/952583ecac836f843f50b785c7cb283d/raw/5718ebd8c9b4f9a549746094877a97e7796752eb/solvelinmod.py')

from pwn import * 

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

# print(newpass)
while True:
	# io = remote("183.91.11.30", 666)
	io = process(["python3", "server.py"])
	register("dat", password.hex())
	token_admin = get_token("admin")
	token = get_token("dat")
	value = sum([x*b for b,x in zip(token, password)]) % q1
	v = var(" ".join(f'v{i}' for i in range(128)))
	equa = 0
	bounds = {}
	for i in range(128):
		bounds[v[i]] = 128*100
		equa += v[i] * token_admin[i]

	sol = solve_linear_mod([(equa ==value,q1)], bounds)
	sol = [int(sol[i]) for i in v]
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
	newpass = bytes(newpass)
	block = [newpass[i : i+BLOCK_LEN] for i in range(0, len(newpass), BLOCK_LEN)]
	new_block = []
	for i in range(100):
		if not all(x == 0 for x in block[i][:-1]):
			new_block.append(block[i])
	newpass = b''.join(new_block)
	register("aaa", newpass.hex())

	register("admin", newpass.hex(), login=True)
	if b'Welcome' in io.recvline():
		io.interactive()
	else:
		io.close()


# 39731139662547065548854550308900512214066612509051171641369079170957336402536230662789994475195258705771171218232706461704327037872226663304344156661539595419173549199355656485560505042133981683277859456288170944973452119610267889997831809473466306730608292872058899247019002645196787592574205304315216770737
# 18254204639575653399244021530741031373647658133852659209966512618370743619735906959538425450749890256667291625534161792736041002516019034817623806290122254757321256067861363284876034678630395939114563801714079285501274679488759257583736247007856004228767960843406344907883210206051952077077019588822816801376

