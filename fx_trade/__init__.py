from gym.envs.registration import register

register(
    id='fx_trade-v0',
    entry_point='fx_trade.env:trade'
)