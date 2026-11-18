"""Tests for the Machine Shop timeline."""

# ruff: noqa: D101, D103, D107
import pytest

from mesa.examples.experimental.machine_shop.agents import (
    RepairAction,
)
from mesa.examples.experimental.machine_shop.model import MachineShop
from mesa.experimental.actions import ActionState


def test_production_resumes_after_repair():
    model = MachineShop()
    machine = model.machine
    production = machine.current_action

    model.run_until(4)

    assert production.state == ActionState.INTERRUPTED
    assert production.progress == pytest.approx(0.4)

    model.run_until(7)

    assert production.state == ActionState.ACTIVE
    assert production.progress == pytest.approx(0.4)
    assert machine.current_action is production
    assert machine.is_broken is False


def test_production_completes_after_resumption():
    model = MachineShop()
    production = model.machine.current_action

    model.run_until(15.5)

    assert production.state == ActionState.ACTIVE

    model.run_until(16)

    assert production.state == ActionState.COMPLETED
    assert production.progress == pytest.approx(1.0)
    assert model.machine.current_action is None


def test_machine_recovers_from_two_breakdowns():
    model = MachineShop()
    machine = model.machine
    production = machine.current_action

    model.run_until(9)

    # Second breakdown has occurred.
    assert production.state == ActionState.INTERRUPTED
    assert production.progress == pytest.approx(0.6)
    assert isinstance(machine.current_action, RepairAction)
    assert machine.is_broken is True

    model.run_until(12)

    # Production resumes from 60%.
    assert production.state == ActionState.ACTIVE
    assert production.progress == pytest.approx(0.6)
    assert machine.current_action is production

    model.run_until(16)

    # Original production action completes.
    assert production.state == ActionState.COMPLETED
    assert production.progress == pytest.approx(1.0)
    assert machine.current_action is None


class FailingRepairAction(RepairAction):
    def __init__(self, machine):
        super().__init__(machine)
        self.start_requirements = [lambda agent: False]


def test_failed_repair_does_not_resume_production():
    model = MachineShop()
    machine = model.machine
    production = machine.current_action

    machine.is_broken = True
    machine.interrupted_job = production

    failed_repair = FailingRepairAction(machine)
    assert machine.interrupt_for(failed_repair) is False

    model.run_until(model.time + 1)

    assert failed_repair.state == ActionState.FAILED
    assert machine.current_action is None
    assert production.state == ActionState.INTERRUPTED
    assert machine.is_broken is True
