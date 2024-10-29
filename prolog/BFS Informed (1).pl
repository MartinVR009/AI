% Define Rooms
room(b1).
room(b2).

% Define Connections
connection(b1, b2).
connection(b2, b1).

% Define Box Colors
box(red).
box(blue).

% (Robot Location, What robot is carrying, [boxes in b1], [boxes in b2]).
initial_state(state(b1, none, [], [red, blue])).

goal_state(state(b2, none, [red, blue], [])).

% Move without carrying anything
action(state(From, none, B1, B2), state(To, none, B1, B2)) :-
    connection(From, To).

% Move while carrying a box
action(state(From, Holding, B1, B2), state(To, Holding, B1, B2)) :-
    connection(From, To).

% Pick Up Actions
action(state(Room, none, B1, B2), state(Room, Box, B1Rest, B2)) :-
    Room = b1,
    member(Box, B1),
    delete(B1, Box, B1Rest).

action(state(Room, none, B1, B2), state(Room, Box, B1, B2Rest)) :-
    Room = b2,
    member(Box, B2),
    delete(B2, Box, B2Rest).

% Drop Actions
action(state(Room, Box, B1, B2), state(Room, none, [Box | B1], B2)) :-
    Room = b1,
    Box \= none.

action(state(Room, Box, B1, B2), state(Room, none, B1, [Box | B2])) :-
    Room = b2,
    Box \= none.

% Heuristic based on how many boxes are in the second room
heuristic(state(_, _, _, B2), H) :-
    length(B2, H). 

% Informed BFS
bfs(Start, Path) :-
    bfs_informed([[Start]], RevPath),
    reverse(RevPath, Path).

bfs_informed([[State | Path] | _], [State | Path]) :-
    goal_state(State).

bfs_informed([[State | Path] | Rest], FinalPath) :-
    findall(
        [NextState, State | Path],
        (action(State, NextState), \+ member(NextState, [State | Path])),
        NewPaths
    ),
    % Calculate heuristics and order all new paths from the current state
    order_paths(NewPaths, OrderedPaths),
    % Recursive call for all new paths
    append(Rest, OrderedPaths, UpdatedQueue),
    bfs_informed(UpdatedQueue, FinalPath).

% Calculate the heuristic for each path and sort them
order_paths(Paths, OrderedPaths) :-
    maplist(wrapper, Paths, PathsWithHeuristic),
    keysort(PathsWithHeuristic, Sorted),
    pairs_values(Sorted, OrderedPaths).

% Wraps the path in a tuple with its heuristic value
wrapper([FinalState, InitialState | RestOfPath], Heuristic - [FinalState, InitialState | RestOfPath]) :-
    heuristic(FinalState, Heuristic).

% Solve the problem
solve(Path) :-
    initial_state(Start),
    bfs(Start, Path).

% Execute the solver and display the solution
run_solver :-
    solve(Path),
    print_solution(Path).

% Print Solution
print_solution([]).
print_solution([State | Rest]) :-
    write(State), nl,
    print_solution(Rest).
