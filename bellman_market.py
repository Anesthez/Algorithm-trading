import States


class Bellman:

    def __init__(self, learn_rate, quantile_size):
        self.quantile_size = quantile_size
        self.learn_rate = learn_rate
        self.states = []
        self.prob = {}
        self.Q = []

    def __read_states__(self, size):
        file = open('market_data')
        file.readline().strip()
        if size > 200000:
            raise EOFError
        line = file.readline().strip()
        content = line.split(',')
        for i in range(size):
            next_line = file.readline().strip()
            next_content = next_line.split(',')

            ask_price_change = float(content[11]) - float(next_content[11])
            bid_price_change = float(content[10]) - float(next_content[10])
            ask_change = float(content[5]) - float(next_content[5])
            bid_change = float(content[0]) - float(next_content[0])
            order_cancel = float(content[12])
            for a_quantile in range(self.quantile_size):
                for b_quantile in range(self.quantile_size):
                    for place in range(3):
                        for enter in range(4):
                            state = States.States(
                                float(content[5]),
                                float(content[0]),
                                a_quantile,
                                b_quantile,
                                place,
                                enter - 1)

                            self.states.append(state)
                            if i != size - 1:
                                self.prob[state] = self.__next_state__(ask_price_change, bid_price_change, state,
                                                                       ask_change, bid_change, enter,
                                                                       float(content[11]), float(content[10]), i,
                                                                       order_cancel)
            content = next_content
        self.Q = [[0 for _ in range(5)] for _ in range(len(self.states))]
        file.close()

    def __next_state__(self, ask_price_change, bid_price_change, state,
                       ask_quantity_change, bid_quantity_change, enter_price,
                       ask_price, bid_price, curr, order_cancel):
        def calc_ask_quantile():
            if int(state.ask_quant + ask_quantity_change) == 0:
                return 0
            elif ask_quantity_change < 0 and order_cancel <= 0:
                return int((state.ask_quant / self.quantile_size) * state.ask_quantile + ask_quantity_change) / \
                       int(state.ask_quant + ask_quantity_change)
            elif order_cancel >= 0:
                return int((state.ask_quant / self.quantile_size) * state.ask_quantile) / \
                       int(state.ask_quant + ask_quantity_change)
            else:
                return int((state.ask_quant / self.quantile_size) * state.ask_quantile) / \
                       int(state.ask_quant + ask_quantity_change)

        def calc_bid_quantile():
            if int(state.bid_quant + bid_quantity_change) == 0:
                return 0
            elif bid_quantity_change < 0 <= order_cancel:
                return int((state.bid_quant / self.quantile_size) * state.bid_quantile + bid_quantity_change) / \
                       int(state.bid_quant + bid_quantity_change)
            elif order_cancel <= 0:
                return int((state.bid_quant / self.quantile_size) * state.bid_quantile) / \
                       int(state.bid_quant + bid_quantity_change)
            else:
                return int((state.bid_quant / self.quantile_size) * state.bid_quantile) / \
                       int(state.bid_quant + bid_quantity_change)

        def calc_state_num(ask_quantile, bid_quantile, anchor, place):
            return int(self.quantile_size * self.quantile_size * 4 * 3 * (curr + 1) +
                       ask_quantile * self.quantile_size * 4 * 3 + bid_quantile * 4 * 3
                       + anchor * 3 + place)

        def place_check(check_place):
            if check_place == 0:
                return 0
            else:
                return (ask_price - bid_price) // 5

        CANCEL_BID = 0
        ADD_BID = 1
        WAIT = 2
        CANCEL_ASK = 3
        ADD_ASK = 4
        next_states = [-1 for _ in range(5)]
        ADD_SIZE = self.quantile_size - 1
        WAIT_SIZE = self.quantile_size

        next_place = state.place

        if state.ask_quantile > 0 > ask_price_change:
            if state.bid_quantile == 0:
                next_states[WAIT] = calc_state_num(WAIT_SIZE, 0, enter_price, next_place)
                next_states[CANCEL_ASK] = calc_state_num(0, 0, enter_price, next_place)
                next_states[ADD_BID] = calc_state_num(WAIT_SIZE, ADD_SIZE, enter_price, next_place)
                return next_states
            elif state.bid_quantile > 0 and bid_price_change > 0:
                next_states[WAIT] = calc_state_num(WAIT_SIZE, WAIT_SIZE, enter_price, next_place)
                next_states[CANCEL_ASK] = calc_state_num(0, WAIT_SIZE, enter_price, next_place)
                next_states[CANCEL_BID] = calc_state_num(WAIT_SIZE, 0, enter_price, next_place)
                return next_states
            elif state.bid_quantile > 0 > bid_price_change:
                next_place = next_place + 1
                enter_price = place_check(next_place)
                next_states[WAIT] = calc_state_num(WAIT_SIZE, 0, enter_price, next_place)
                next_states[CANCEL_ASK] = calc_state_num(0, 0, enter_price, next_place)
                next_states[ADD_BID] = calc_state_num(WAIT_SIZE, ADD_SIZE, enter_price, next_place)
                return next_states
            elif state.bid_quantile > 0:
                new_bid_quantile = calc_bid_quantile()
                next_states[WAIT] = calc_state_num(WAIT_SIZE, new_bid_quantile, enter_price, next_place)
                next_states[CANCEL_ASK] = calc_state_num(0, new_bid_quantile, enter_price, next_place)
                next_states[CANCEL_BID] = calc_state_num(WAIT_SIZE, 0, enter_price, next_place)
                return next_states
        elif state.ask_quantile > 0 and ask_price_change > 0:
            next_place = next_place - 1
            enter_price = place_check(next_place)
            if state.bid_quantile == 0:
                next_states[WAIT] = calc_state_num(0, 0, enter_price, next_place)
                next_states[ADD_ASK] = calc_state_num(ADD_SIZE, 0, enter_price, next_place)
                next_states[ADD_BID] = calc_state_num(0, ADD_SIZE, enter_price, next_place)
                return next_states
            elif state.bid_quantile > 0 and bid_price_change > 0:
                next_states[WAIT] = calc_state_num(0, WAIT_SIZE, enter_price, next_place)
                next_states[ADD_ASK] = calc_state_num(ADD_SIZE, WAIT_SIZE, enter_price, next_place)
                next_states[CANCEL_BID] = calc_state_num(0, 0, enter_price, next_place)
                return next_states
            elif state.bid_quantile > 0 > bid_price_change:
                next_place = next_place + 1
                enter_price = place_check(next_place)
                next_states[WAIT] = calc_state_num(0, 0, enter_price, next_place)
                next_states[ADD_ASK] = calc_state_num(ADD_SIZE, 0, enter_price, next_place)
                next_states[ADD_BID] = calc_state_num(0, ADD_SIZE, enter_price, next_place)
                return next_states
            elif state.bid_quantile > 0:
                new_bid_quantile = calc_bid_quantile()
                next_states[WAIT] = calc_state_num(0, new_bid_quantile, enter_price, next_place)
                next_states[ADD_ASK] = calc_state_num(ADD_SIZE, new_bid_quantile, enter_price, next_place)
                next_states[CANCEL_BID] = calc_state_num(0, 0, enter_price, next_place)
                return next_states
        elif state.ask_quantile > 0:
            new_ask_quantile = calc_ask_quantile()
            if state.bid_quantile == 0:
                next_states[WAIT] = calc_state_num(new_ask_quantile, 0, enter_price, next_place)
                next_states[CANCEL_ASK] = calc_state_num(0, 0, enter_price, next_place)
                next_states[ADD_BID] = calc_state_num(new_ask_quantile, ADD_SIZE, enter_price, next_place)
                return next_states
            elif state.bid_quantile > 0 and bid_price_change > 0:
                next_states[WAIT] = calc_state_num(new_ask_quantile, WAIT_SIZE, enter_price, next_place)
                next_states[CANCEL_ASK] = calc_state_num(0, WAIT_SIZE, enter_price, next_place)
                next_states[CANCEL_BID] = calc_state_num(new_ask_quantile, 0, enter_price, next_place)
                return next_states
            elif state.bid_quantile > 0 > bid_price_change:
                enter_price = next_place
                next_states[WAIT] = calc_state_num(new_ask_quantile, 0, enter_price, next_place)
                next_states[CANCEL_ASK] = calc_state_num(0, 0, enter_price, next_place)
                next_states[ADD_BID] = calc_state_num(new_ask_quantile, ADD_SIZE, enter_price, next_place)
                return next_states
            elif state.bid_quantile > 0:
                new_bid_quantile = calc_bid_quantile()
                next_states[WAIT] = calc_state_num(new_ask_quantile, new_bid_quantile, enter_price, next_place)
                next_states[CANCEL_ASK] = calc_state_num(0, new_bid_quantile, enter_price, next_place)
                next_states[CANCEL_BID] = calc_state_num(new_ask_quantile, 0, enter_price, next_place)
                return next_states
        elif state.ask_quantile == 0:
            if state.bid_quantile == 0:
                next_states[WAIT] = calc_state_num(0, 0, enter_price, next_place)
                next_states[ADD_ASK] = calc_state_num(ADD_SIZE, 0, enter_price, next_place)
                next_states[ADD_BID] = calc_state_num(0, ADD_SIZE, enter_price, next_place)
                return next_states
            elif state.bid_quantile > 0 and bid_price_change > 0:
                next_states[WAIT] = calc_state_num(0, WAIT_SIZE, enter_price, next_place)
                next_states[ADD_ASK] = calc_state_num(ADD_SIZE, WAIT_SIZE, enter_price, next_place)
                next_states[CANCEL_BID] = calc_state_num(0, 0, enter_price, next_place)
                return next_states
            elif state.bid_quantile > 0 > bid_price_change:
                next_place += 1
                enter_price = place_check(next_place)
                next_states[WAIT] = calc_state_num(0, 0, enter_price, next_place)
                next_states[ADD_ASK] = calc_state_num(ADD_SIZE, 0, enter_price, next_place)
                next_states[ADD_BID] = calc_state_num(0, ADD_SIZE, enter_price, next_place)
                return next_states
            elif state.bid_quantile > 0:
                new_bid_quantile = calc_bid_quantile()
                next_states[WAIT] = calc_state_num(0, new_bid_quantile, enter_price, next_place)
                next_states[ADD_ASK] = calc_state_num(ADD_SIZE, new_bid_quantile, enter_price, next_place)
                next_states[CANCEL_BID] = calc_state_num(0, 0, enter_price, next_place)
                return next_states

    def __update__(self, learn_rate, gamma):
        for i in range(len(self.states) - 3 * 4 * self.quantile_size * self.quantile_size - 1, -1, -1):
            for j in range(5):
                next_state_num = self.prob[self.states[i]][j]
                if next_state_num == -1:
                    self.Q[i][j] = 0
                    continue
                self.Q[i][j] += ((self.states[i].get_reward(self.states[next_state_num]) +
                                  max(self.Q[next_state_num])) * gamma - self.Q[i][j]) * learn_rate
