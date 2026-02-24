# High Performance Tool calling

In this example we will demonstrate agents sharing a set of nodes within a batch job to drive expensive
MD simulations via tool calling. We will mock the functionality of the agents as well as the tools and
focus on the specifics of setting up the infrastructure for resource sharing.

This example set uses:

* `agentic_blueprint_catalog/agents/director.py` -> Director agent that uses Parsl to launch mocked MD
    simulations both as an individial call and in batches.
* `agentic_blueprint_catalog/hpc_hierarchical/minimal.py` -> Minimal example to demonstrate the pattern
* `agentic_blueprint_catalog/hpc_hierarchical/complete.py` -> A more complete example to demonstrate
    complexity similar to a production setup.
* `agentic_blueprint_catalog/hpc_hierarchical/aurora.config.j2` -> Globus Compute Endpoint config for
    Aurora@ALCF that was used for testing. This jinja templated yaml config would go in your
    `~/.globus_compute/<MEP>/user_config_template.yaml.j2`

Here are some key features:
1. Two DirectorAgents will be launched via GlobusCompute to run on the lead node of a 4 node batch job.
2. We logically partition the 4 nodes into 2 partitions of 2 nodes each.
3. Each DirectorAgent will own one logical partition and launch MD simulation tasks using Parsl for task execution
   and resource orchestration.
    
    Step 1. Launch 2 Directors onto Node1
    ``` 
    +-----------------------------AURORA@ANL------------------------------+
    +   +------------+   +---------------BATCH JOB-(4 Nodes)----------+   |
    +   | GCompute --+-->+  +-------Node1------+ +-------Node1------+ |   |
    +   +------------+   |  | Director1        | |                  | |   |
    +                    |  | Director2        | |                  | |   |
    +                    |  +------------------+ +------------------+ |   |
    +                    |                                            |   |
    +                    |  +-------Node2------+ +-------Node3------+ |   |
    +                    |  |                  | |                  | |   |
    +                    |  |                  | |                  | |   |
    +                    |  +------------------+ +------------------+ |   |
    +-----------------------------AURORA@ANL------------------------------+
    ```
    Step 2. Launch a ParslExecutor on each of the logical paritions of the batch job
    ```
    +-----------------------------AURORA@ANL------------------------------+
    +   +------------+   +---------------BATCH JOB-(4 Nodes)----------+   |
    +   | GCompute --+-->+  +-------Node1------+ +-------Node1------+ |   |
    +   +------------+   |  | D1---> +------PARSL POOL 1--------+   | |   |
    +                    |  | D2     +--------------------------+   | |   |
    +                    |  +--+---------------+ +------------------+ |   |
    +                    |     |                                      |   |
    +                    |  +--+----Node2------+ +-------Node3------+ |   |
    +                    |  |  +---> +------PARSL POOL 2--------+   | |   |
    +                    |  |        +--------------------------+   | |   |
    +                    |  +------------------+ +------------------+ |   |
    +-----------------------------AURORA@ANL------------------------------+
    ```


