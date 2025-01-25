from typing import Optional


def validate_algorithm(algorithm: Optional[str], team_size: Optional[int]) -> Optional[str]:
    if algorithm is None:
        return None

    if team_size < 2:
        raise ValueError("Size of the team (team_size) must be not less than 2.")

    steps = algorithm.split()
    valid_steps = {"B", "P", "T"}

    for index, step in enumerate(steps):        
        if not all(char in valid_steps for char in step):
            raise ValueError(f"Step '{step}' containings incorrect symbols. Available only these: {', '.join(valid_steps)}.")

        if step != "T" and len(step) != team_size:
            raise ValueError(f"Size of the step '{step}' must be equal to team size ({team_size=}).")

        if step == "T" and index != len(steps) - 1:
            raise ValueError("Step 'T' (tiebreak) can be only at the last step of algorithm.")

        if "T" in step and len(step) > 1:
            raise ValueError(f"Step 'T' must be separated from algorithm ({step=})")

    return algorithm


def validate_teams_count(team_size: int) -> Optional[int]:
    if team_size is None:
        return None

    if team_size < 2 or team_size > 16:
        raise ValueError(f"Team size should be in between 2 and 16 ({team_size=})")
    
    return team_size
