
from bellman_market import Bellman

learn_rate = 1
n_quantiles = 5
n_events = 200000
gamma = 0.98

b = Bellman(learn_rate, n_quantiles) 
b.__read_states__(n_events) 

print(len(b.prob))
#for s in b.states[29679:29699]:
#	print(s,(b.prob[s]))

b.__update__(learn_rate,gamma) 
print(len(b.Q))
print(len(b.Q[0]))

def get_state_id(curr,ask_quantile,bid_quantile,anchor,place):
	return int(  n_quantiles  * n_quantiles * 4 * 3 * curr  +
				 ask_quantile * n_quantiles * 4 * 3 + 
				 bid_quantile * 4 * 3 + anchor * 3 + place)

for i in range(n_events):

	#Extract  enter_price = na(0); pos =0 
	for qa in range(5):
		for qb in range(5):
			sid = get_state_id(i,qa,qb,0,0)
			print(qa,qb,i,sid,b.Q[sid])

