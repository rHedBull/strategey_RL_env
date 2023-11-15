from simulation_run import simulation_run

# Create a simulation instance
sim_run = simulation_run(2, "pick-test", 100)

# Run the simulation
sim_run.setup_run()
sim_run.run_calculation()
sim_run.load_from_file("pick-test")
sim_run.run_calculation()

