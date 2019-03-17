from gym.envs.registration import register

register(
    id='fx_trade_train-v0',
    entry_point='fx_trade.env:trade_train'
)
register(
    id='fx_trade_test-v0',
    entry_point='fx_trade.env:trade_test'
)