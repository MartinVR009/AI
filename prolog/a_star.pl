% Define Rooms
room(b1).
room(b2).
room(b3).

% Define Connections
connection(b1, b2).
connection(b2, b3).
connection(b3, b1).

% (Robot Location, What robot is carrying, [boxes in b1], [boxes in b2], [boxes in b3], Number of movements).
initial_state(state(b3, none, [red], [blue], [], 0)).

goal_state(state(b2, none, [], [], [red, blue], _)). % We don't care about the number of movements in the goal state

% Move without carrying anything
action(state(From, none, B1, B2, B3, Moves), state(To, none, B1, B2, B3, NewMoves)) :-
    connection(From, To),
    NewMoves is Moves + 1.

% Move while carrying a box
action(state(From, Holding, B1, B2, B3, Moves), state(To, Holding, B1, B2, B3, NewMoves)) :-
    connection(From, To),
    NewMoves is Moves + 1.

% Pick up actions
action(state(Room, none, [Box | RestB1], B2, B3, Moves), state(Room, Box, RestB1, B2, B3, Moves)) :-
    Room = b1.

action(state(Room, none, B1, [Box | RestB2], B3, Moves), state(Room, Box, B1, RestB2, B3, Moves)) :-
    Room = b2.

action(state(Room, none, B1, B2, [Box | RestB3], Moves), state(Room, Box, B1, B2, RestB3, Moves)) :-
    Room = b3.

% Drop actions
action(state(Room, Box, B1, B2, B3, Moves), state(Room, none, [Box | B1], B2, B3, Moves)) :-
    Room = b1,
    Box \= none.

action(state(Room, Box, B1, B2, B3, Moves), state(Room, none, B1, [Box | B2], B3, Moves)) :-
    Room = b2,
    Box \= none.

action(state(Room, Box, B1, B2, B3, Moves), state(Room, none, B1, B2, [Box | B3], Moves)) :-
    Room = b3,
    Box \= none.

% Heuristic and cost combined (f = g + h)
heuristic_cost(state(RobotRoom, _, B1, B2, _, Moves), FCost) :-
    length(B1, B1Count),          % Number of boxes in b1
    length(B2, B2Count),          % Number of boxes in b2
    BoxesNotInB3 is B1Count + B2Count, % Total number of boxes not in b3
    (RobotRoom \= b2 -> RobotPenalty = 1; RobotPenalty = 0), % Penalty if robot is not in b2
    FCost is (BoxesNotInB3 + RobotPenalty)+ Moves. % Heuristic value

% A* Algorithm
a_algo(Start, Path) :-
    a_star([[Start]], RevPath),
    reverse(RevPath, Path).

a_star([[State | Path] | _], [State | Path]) :-
    goal_state(State).

a_star([[State | Path] | Rest], FinalPath) :-
    findall(
        [NextState, State | Path],
        (action(State, NextState), \+ member(NextState, [State | Path])),
        NewPaths
    ),
    % Calculate heuristics and order all new paths from the current state
    order_paths(NewPaths, OrderedPaths),
    % Recursive call for all new paths
    append(Rest, OrderedPaths, UpdatedQueue),
    a_star(UpdatedQueue, FinalPath).

% Calculate the heuristic for each path and sort them
order_paths(Paths, OrderedPaths) :-
    maplist(wrapper, Paths, PathsWithHeuristic),
    keysort(PathsWithHeuristic, Sorted),
    pairs_values(Sorted, OrderedPaths).

% Wrapper that uses the heuristic directly
wrapper([FinalState, InitialState | RestOfPath], FCost - [FinalState, InitialState | RestOfPath]) :-
    heuristic_cost(FinalState, FCost).

% Solve the problem
solve(Path) :-
    initial_state(Start),
    a_algo(Start, Path).

% Execute the solver and display the solution
run_solver :-
    solve(Path),
    print_solution(Path).

% Print Solution
print_solution([]).
print_solution([State | Rest]) :-
    write(State), nl,
    print_solution(Rest).
