from gym.envs.registration import register

register(
    id='fceux-v0',
    entry_point='gym_foo.envs:FceuxEnv',
)
