* Running
You may need to install dependencies with `pip install fastapi`, `pdm add fastapi` etc. I neglected to include a full `requirements.txt` since the only requirements are `fastapi` and things like `random`, `uuid` etc that are in the standard library. 

Run with `fastapi dev knots_server.py`. Visit `localhost:8000/game/init` to play. Using the gameid returned there you can go to `game/{game_id}/move?x=i&y=j` specify x and y as query parameters where `i` and `j` are integers 1-3. After your move the computer player will move automatically (if it can) and return the state of the game after. `game/{game_id}/state` shows you the current state of that game id, `game/list` shows you games your host has created this session. `game/test` and `/game/test/computer_win` run quick example games (especially as it's hard to make let computer win with only random moves)

* Time spend
about 4 hours, I didn't use a stopwatch but roughly two days of 2 hour sessions

* Assumptions
an only 3x3 tic-tac-toe grid. The moving, history, init-ing should all be size agnostic and could work with any size grid, but the winstate check and computer moves assume only 3x3. I started off thinking that each function would be able to handle arbitrary sized boards but ran out of time getting winstate checking to that point and ended up with a somewhat brute force approach to checking for a win. 

* Trade-offs
Main one is that full board history is generated only when you ask for it, by hitting the `state` endpoint or when a game has concluded. The idea here is that an average user will only request state one, maybe two, times (when the game has concluded). This way while large numbers of players all init and play games concurrently we save history using much less memory (only the player character and x,y coordinates rather than the full 2D list). In a "pathologic" user case where a user requests state many times in a row or after every single move this will be resource intensive as the server recreates the full state history every single time. Given more time or a request to production-ify this code I would add a memoization component to history generation where generated full history is stored in the `Game` object and further requests to generate history would check for existing history and only generate new not-yet-found history.

A number of quick working trade-offs were made; logging is done via simple `print` statements that just show up in the dev console of fastapi rather than a full fledged logging implementation/harness. There are only two tests which have to be manually run rather than with a test framework and the tests themselves are simple e2e nose tests more than actual unit tests. These were helpful to me for developing (rather than manually marking out moves each time) but would be inadequate for real production code.
    
* Anything else
This was my first time ever using FastAPI, it was an impressively quick process to get started. If there's anything I've done here particularly non-canonical or egregiously against the FastAPI ethos I would love to know.  
