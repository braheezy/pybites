# Prerequisites

1. \*Nix-like environment

    The scripts below are shell scripts.

2. Python 3

   To check, `python3 -V` in a terminal.

3. MongoDB

   Install it for your OS. [MongoDB Install Instructions](https://docs.mongodb.com/manual/installation/)

   MongoDB must be running at the same MONGO_URI used in `config.py` for the application to use the database.

# Install

In the root of the project, run the install script:

`./install.sh`

# Usage

To run the entire application:

`./dev.sh`

To stop:

`./kill.sh`
