
import re

ETH_WALLET='0xf6daa81109dc170e4145d8661c3f50a1e32d348b'
ETH_POOL='ethash.poolbinance.com:1800'
ETH_WORKER='homenix.001:123456'

URL = 'stratum1+tcp://' + ETH_WALLET + '.' + ETH_WORKER + '@' + ETH_POOL


r = re.search( r'^(.*)@(.*)$', URL, re.M|re.I)



r = re.search( r'^([a-zA-Z0-9\\+]{1,})://(.*)$', ETH_WORKER, re.M|re.I)

r1 = re.search( r'^(.*).(.*):(.*)$', ETH_WORKER, re.M|re.I)
r2 = re.search( r'^(.*):(.*)$', ETH_WORKER, re.M|re.I)
r3 = re.search( r'^(.*).(.*)$', ETH_WORKER, re.M|re.I)


print(f'{r1}')
print(f'{r2}')
print(f'{r3}')

