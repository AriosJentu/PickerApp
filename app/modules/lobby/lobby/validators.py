from typing import Optional

from app.core.config import settings


class LobbyValidator:

    @staticmethod
    def teams_count(teams_count: Optional[int]) -> Optional[int]:
        if teams_count is None:
            return None

        if not (settings.MIN_TEAMS_COUNT <= teams_count <= settings.MAX_TEAMS_COUNT):
            raise ValueError(f"Teams count should be in between {settings.MIN_TEAMS_COUNT} and {settings.MAX_TEAMS_COUNT} ({teams_count=})")
        
        return teams_count
    

    @staticmethod
    def algorithm(algorithm_str: Optional[str], teams_count: Optional[int]) -> Optional[str]:
        if algorithm_str is None:
            return None
        
        if not algorithm_str.strip():
            raise ValueError("Algorithm should contain at least one step")

        teams_count = LobbyValidator.teams_count(teams_count)
        steps = algorithm_str.split()
        valid_steps = {"B", "P", "T"}

        for index, step in enumerate(steps):        
            if not all(char in valid_steps for char in step):
                raise ValueError(f"Step '{step}' containings incorrect symbols. Available only these: {', '.join(valid_steps)}.")

            if step != "T" and len(step) != teams_count:
                raise ValueError(f"Size of the step '{step}' must be equal to teams count ({teams_count=}).")

            if step == "T" and index != len(steps) - 1:
                raise ValueError("Step 'T' (tiebreak) can be only at the last step of algorithm.")

            if "T" in step and len(step) > 1:
                raise ValueError(f"Step 'T' must be separated from algorithm ({step=})")

        return algorithm_str
    

    @staticmethod
    def name(name: Optional[str], obj_type: str = "Lobby") -> Optional[str]:
        if name is None:
            return None
        
        if not name.strip():
            raise ValueError(f"{obj_type} name cannot be empty")
        
        return name
