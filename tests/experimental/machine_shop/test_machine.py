"""Tests for the Machine Shop machine agent."""

# ruff: noqa: D103
from mesa.examples.experimental.machine_shop.model import MachineShop


def test_machine_initialization():
    model = MachineShop()
    machine = model.machine

    assert machine.is_broken is False
    assert machine.interrupted_job is None


def test_duplicate_breakdown_is_ignored():
    model = MachineShop()
    machine = model.machine

    machine.breakdown()
    repair = machine.current_action

    machine.breakdown()

    assert machine.current_action is repair
    assert machine.is_broken is True
