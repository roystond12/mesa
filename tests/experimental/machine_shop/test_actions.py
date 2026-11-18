"""Tests for Machine Shop production and repair actions."""

# ruff: noqa: D103
import pytest

from mesa.examples.experimental.machine_shop.agents import (
    ProductionAction,
    RepairAction,
)
from mesa.examples.experimental.machine_shop.model import MachineShop
from mesa.experimental.actions import ActionState


def test_production_starts():
    model = MachineShop()
    machine = model.machine

    assert isinstance(machine.current_action, ProductionAction)
    assert machine.current_action.state == ActionState.ACTIVE


def test_repair_preempts_production():
    model = MachineShop()
    machine = model.machine
    production = machine.current_action

    machine.breakdown()

    assert production.state == ActionState.INTERRUPTED
    assert production.progress == pytest.approx(0.0)
    assert isinstance(machine.current_action, RepairAction)
    assert machine.is_broken is True


def test_repair_has_higher_priority_than_production():
    model = MachineShop()
    machine = model.machine

    production = machine.current_action
    repair = RepairAction(machine)

    assert machine.interrupt_for(repair) is True
    assert repair.priority > production.priority
    assert production.state == ActionState.INTERRUPTED
    assert machine.current_action is repair


def test_repair_is_not_interruptible():
    model = MachineShop()
    machine = model.machine

    machine.breakdown()
    repair = machine.current_action

    production = ProductionAction(
        machine,
        duration=5,
        job_name="Job B",
    )

    assert machine.interrupt_for(production) is False
    assert machine.current_action is repair
    assert repair.state == ActionState.ACTIVE
