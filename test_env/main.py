from RL_env.MapEnvironment import MapEnvironment
from test_env.Player import Player
from test_env.Agent import Agent

import pygame

Rendering = True
screen_size = 1000
num_agents = 2
max_steps = 300


def main():
    screen = None

    pygame.init()

    if Rendering:
        # init pygame
        screen = pygame.display.set_mode((screen_size, screen_size))
        pygame.display.set_caption('Agent-based Landmass Generation')
        screen.fill((0, 0, 0))

    env = MapEnvironment("./test_env/env_settings.json", num_agents, Rendering, screen)

    if Rendering:
        env.render()
        pygame.display.flip()

    # setup my agents
    agents = [Player()]
    for i in range(num_agents - 1):
        agent = Agent(i)
        agents.append(agent)

    # run the game loop
    done = False
    step = 0
    # list of agents that are still running, by index in agents list
    running_agents = [i for i in range(num_agents)]
    while not done and step < max_steps:

        # get actions from agents
        agent_actions = []
        for agent in agents:
            if agent.state == 'Done':
                agent_actions.append('None')
                continue
            # if agent is a player, get action from keyboard
            if isinstance(agent, Player):
                action = agent.get_action(pygame)
                print("Player chose action {}".format(action))
            else:
                possible_actions = ['Move Up', 'Move Down', 'Move Left', 'Move Right', 'Claim']
                action = agent.get_action(possible_actions)
                print("Agent {} chose action {}".format(agent.id, action))
            agent_actions.append(action)

        state, reward, dones, info = env.step(agent_actions)

        for i, done in zip(running_agents, dones):
            if done:
                print("Agent {} is done".format(i))
                agents[i].state = 'Done'

        running_agents = [agent for agent, done in zip(running_agents, dones) if not done]

        env.render()
        # flip the display
        pygame.display.flip()

        # check if the game is over
        if running_agents == 0:
            done = True
            print("All agents are done")
        step += 1

    print("Game Terminated")
    if Rendering:
        # keep the window open until the user closes it manually
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
        pygame.quit()


if __name__ == "__main__":
    main()
