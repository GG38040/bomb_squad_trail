import pytest
from states import StateManager, GameState


def test_change_state_updates_current_and_previous():
    sm = StateManager()
    assert sm.current_state == GameState.MENU
    assert sm.previous_state is None

    sm.change_state(GameState.TRAVEL)
    assert sm.previous_state == GameState.MENU
    assert sm.current_state == GameState.TRAVEL

    sm.change_state(GameState.MINIGAME)
    assert sm.previous_state == GameState.TRAVEL
    assert sm.current_state == GameState.MINIGAME

