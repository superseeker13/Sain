from gym.envs.registration import register

register(
    id='nintaco-v0',
    entry_point='gym_foo.envs:NintacoEnv',
)
