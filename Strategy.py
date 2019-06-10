class Strategy():
    def __init__(self, df, warmup, user_config='', default_config_file=''):
        raise NotImplementedError()

    def load_config(self, user_config, default_config_file=''):
        raise NotImplementedError()

    def add_indicators(self, df):
        raise NotImplementedError()

    def step(self, tup):
        raise NotImplementedError()

    def backtest(self, prempt=False, visualize=False):
        raise NotImplementedError()

    def visualize(self, actions=[]):
        raise NotImplementedError()
