from polyhex.environment.training import CascadiaEnv

env = CascadiaEnv(seed = 0)

print(env._get_obs())

env.render()