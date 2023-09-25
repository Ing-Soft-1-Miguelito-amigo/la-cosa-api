from fastapi import HTTPException


# Function to verify configuration data integrity
def verify_data(game_name, min_players, max_players):
    """
    Verify the integrity of game configuration data.

    Parameters:
    - game_name (str): The name of the game.
    - min_players (int): The minimum number of players.
    - max_players (int): The maximum number of players.

    Raises:
    - HTTPException (status_code=422): If game name is empty, or if min_players is less than 4 or max_players
    is greater than 12.

    Returns:
    - None
    """
    if not game_name:
        raise HTTPException(status_code=422, detail="Game name cannot be empty")

    if min_players < 4:
        raise HTTPException(
            status_code=422, detail="Minimum players cannot be less than 4"
        )

    if max_players > 12:
        raise HTTPException(
            status_code=422, detail="Maximum players cannot be greater than 12"
        )
