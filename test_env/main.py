from RL_env.MapEnvironment import MapEnvironment


def main():
    env = MapEnvironment("./test_env/env_settings.json", 1)
    #env.reset()
    env.render()

    done = False
    while not done:
        action = 0
        #state, reward, done, info = env.step(action)
        env.render()


if __name__ == "__main__":
    main()
