from typing import Tuple, List, Any
from State import State


class SearchProblem:
    """_summary_"""

    def start_state(self) -> State:
        """_summary_

        Raises:
            NotImplementedError: _description_

        Returns:
            Tuple: _description_
        """
        raise NotImplementedError("Override me")

    # Return set of actions possible from |state|.
    def is_end(self, state: State) -> bool:
        """_summary_

        Args:
            state (State): _description_

        Raises:
            NotImplementedError: _description_

        Returns:
            bool: _description_
        """
        raise NotImplementedError("Override me")

    def successors_and_cost(self, state: Tuple, action: Any) -> List[Tuple]:
        """_summary_

        Args:
            state (Tuple): _description_
            action (Any): _description_

        Raises:
            NotImplementedError: _description_

        Returns:
            List[Tuple]: _description_
        """
        raise NotImplementedError("Override me")
