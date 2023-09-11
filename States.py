# 230710 Added str() and repr()

class States:

    def __init__(self, ask_quant, bid_quant, ask_quantile, bid_quantile,
                 place, enter_price):
        self.ask_quant = ask_quant
        self.bid_quant = bid_quant
        self.ask_quantile = ask_quantile
        self.bid_quantile = bid_quantile
        self.place = place
        self.enter_price = enter_price

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"State({self.ask_quant},{self.bid_quant},{self.ask_quantile}," \
               f"{self.bid_quantile},{self.place},{self.enter_price})"

    def get_reward(self, next_state) -> float:

        if next_state.place == 0 and self.place != 0:
            return next_state.enter_price * 5 - 0.02
        elif self.place == 0 and next_state.place != 0:
            return -0.02
        elif (self.place == 0 and next_state.place == 0 and
              self.bid_quantile > 0 and next_state.bid_quantile == 0):
            return next_state.enter_price * 5 - 0.04
        else:
            return 0

