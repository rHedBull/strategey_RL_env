from Map.Map import Map


def main():

    visualization = True

    run_name = "map-test"
    max_steps = 100
    numb_nations = 4

    #simulation_run = Simulation_run(numb_nations, run_name, max_steps)

    # screen = pygame.display.set_mode((800, 600))

    #screen = pygame.display.set_mode((1000, 1000))
    #pygame.display.set_caption('Agent-based Landmass Generation')

    sim_map = Map()
    sim_map.create_map(1000, 1000, show= False)

    """
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Handle other events, like user interactions

        # Update the state of the simulation
        #simulation_run.update()




        # Update the display
        #pygame.display.flip()
    
    # Clean up
    pygame.quit()
    """
if __name__ == "__main__":
    main()

