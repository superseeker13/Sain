from gym.envs.registration import register
import nintaco as tako

register(
    id='nintaco-v0',
    entry_point='gym_foo.envs:NintacoEnv',
)
