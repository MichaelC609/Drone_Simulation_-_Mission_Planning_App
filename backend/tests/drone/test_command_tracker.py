#################################################################################
# test_command_tracker.py:                                                      #    
#   Responsible for testing the functionality for command_tracker.py            #
#   Requirements:                                                               #
#       pytest                                                                  #
#################################################################################

import pytest
from uuid import uuid4
from drone.command_tracker import CommandTracker
from drone.command_tracking import CommandStatusEnum
from drone.commands import TakeoffCommand, TakeoffPayload, LandCommand, LandingPayload

##########Define fixtures##########
@pytest.fixture
def tracker():
    return CommandTracker()


@pytest.fixture
def takeoff_command():
    """
    Fixture that provides a TakeoffCommand with TakeoffPayload for testing.
    
    - Target altitude: 10 meters
    - Takeoff speed: 2 m/s
    - UUID and timestamp are auto-generated
    - Command is not registered; individual tests control registration
    """
    payload = TakeoffPayload(target_altitude=10.0, takeoff_speed=2.0)
    return TakeoffCommand(payload=payload)


##########test successful command registration##########
def test_register_command(tracker, takeoff_command):
    #Verify that a command is registered with the correct initial metadata.
    tracker.register(takeoff_command)
    record = tracker.get_record(takeoff_command.id)

    #assertions
    assert record is not None

    assert record.command_id == takeoff_command.id
    assert record.command_type == takeoff_command.command_type
    assert record.status == CommandStatusEnum.QUEUED
    assert record.created_at == takeoff_command.timestamp

    assert record.started_at is None
    assert record.finished_at is None
    assert record.error_message is None


##########test duplicate command registration##########
def test_register_duplicate_command(tracker, takeoff_command):
    #Verify that the tracker prevents duplicate command registration and raises ValueError.
    tracker.register(takeoff_command)
    
    tracker.mark_running(takeoff_command.id)
    record_after_running = tracker.get_record(takeoff_command.id)
    assert record_after_running.status == CommandStatusEnum.RUNNING
    
    with pytest.raises(ValueError):
        tracker.register(takeoff_command)
    
    record_after_duplicate_attempt = tracker.get_record(takeoff_command.id)
    assert record_after_duplicate_attempt == record_after_running


##########test existing command retrieval##########
def test_get_existing_record(tracker, takeoff_command):
    #Verify that the tracker retrieves the correct record when multiple commands 
    #   of different types are registered.
    land_payload = LandingPayload(landing_speed=1.5)
    land_command = LandCommand(payload=land_payload)
    
    tracker.register(takeoff_command)
    tracker.register(land_command)
    
    record_takeoff = tracker.get_record(takeoff_command.id)
    record_land = tracker.get_record(land_command.id)
    
    #assertions
    assert record_takeoff is not None
    assert record_land is not None
    
    assert record_takeoff.command_id == takeoff_command.id
    assert record_land.command_id == land_command.id
    
    assert record_takeoff.command_type == takeoff_command.command_type
    assert record_land.command_type == land_command.command_type
    
    assert record_takeoff.created_at == takeoff_command.timestamp
    assert record_land.created_at == land_command.timestamp
    
    assert record_takeoff.status == CommandStatusEnum.QUEUED
    assert record_land.status == CommandStatusEnum.QUEUED
    
    assert record_takeoff.command_id != record_land.command_id


##########test correct return for nonexistent command##########
def test_get_nonexistent_record(tracker):
    #Verify that requesting an unknown command returns None.
    random_uuid = uuid4()
    record = tracker.get_record(random_uuid)
    
    assert record is None


##########test duplicate command registration##########
def test_get_record_returns_copy(tracker, takeoff_command):
    #Verify that external components cannot directly modify the tracker's internal records.
    tracker.register(takeoff_command)
    
    retrieved_record = tracker.get_record(takeoff_command.id)
    assert retrieved_record is not None
    assert retrieved_record.status == CommandStatusEnum.QUEUED
    
    retrieved_record.status = CommandStatusEnum.COMPLETED
    
    fresh_record = tracker.get_record(takeoff_command.id)
    assert fresh_record is not None
    assert fresh_record.status == CommandStatusEnum.QUEUED


##########test mark command as running##########
def test_mark_running(tracker, takeoff_command):
    #Verify the transition from QUEUED to RUNNING and correct metadata updates.
    
    tracker.register(takeoff_command)
    original_timestamp = takeoff_command.timestamp
    
    tracker.mark_running(takeoff_command.id)
    record = tracker.get_record(takeoff_command.id)
    
    #assertions
    assert record is not None
    assert record.status == CommandStatusEnum.RUNNING
    assert record.created_at == original_timestamp
    assert record.started_at is not None
    assert record.finished_at is None
    assert record.error_message is None
    
    assert record.command_id == takeoff_command.id
    assert record.command_type == takeoff_command.command_type
    
    assert record.started_at >= record.created_at


##########test mark command as completed##########
def test_mark_completed(tracker, takeoff_command):
    #Verify a successful command execution lifecycle and that lifecycle metadata
    #   is preserved
    tracker.register(takeoff_command)
    original_timestamp = takeoff_command.timestamp
    
    tracker.mark_running(takeoff_command.id)
    running_record = tracker.get_record(takeoff_command.id)
    
    assert running_record is not None
    assert running_record.status == CommandStatusEnum.RUNNING
    assert running_record.started_at is not None
    
    started_at_time = running_record.started_at
    
    tracker.mark_completed(takeoff_command.id)
    completed_record = tracker.get_record(takeoff_command.id)
    
    #assertions
    assert completed_record is not None
    assert completed_record.status == CommandStatusEnum.COMPLETED
    assert completed_record.created_at == original_timestamp
    assert completed_record.started_at == started_at_time
    assert completed_record.finished_at is not None
    assert completed_record.error_message is None
    
    assert completed_record.command_id == takeoff_command.id
    assert completed_record.command_type == takeoff_command.command_type
    
    assert completed_record.finished_at >= completed_record.started_at


##########test mark command as failed##########
def test_mark_failed(tracker, takeoff_command):
    #Verify correct recording of command failure with proper details
    tracker.register(takeoff_command)
    original_timestamp = takeoff_command.timestamp
    
    tracker.mark_running(takeoff_command.id)
    running_record = tracker.get_record(takeoff_command.id)
    
    assert running_record is not None
    assert running_record.status == CommandStatusEnum.RUNNING
    assert running_record.started_at is not None
    
    started_at_time = running_record.started_at
    
    error_message = "Unexpected error during takeoff execution"
    tracker.mark_failed(takeoff_command.id, error_message)
    failed_record = tracker.get_record(takeoff_command.id)
    
    #assertions
    assert failed_record is not None
    assert failed_record.status == CommandStatusEnum.FAILED
    assert failed_record.created_at == original_timestamp
    assert failed_record.started_at == started_at_time
    assert failed_record.finished_at is not None
    assert failed_record.error_message == error_message
    
    assert failed_record.command_id == takeoff_command.id
    assert failed_record.command_type == takeoff_command.command_type
    
    assert failed_record.finished_at >= failed_record.started_at


##########test mark command as rejected##########
def test_mark_rejected(tracker, takeoff_command):
    #Verify that a command rejected before execution is correctly recorded
    tracker.register(takeoff_command)
    original_timestamp = takeoff_command.timestamp
    
    rejection_reason = "Drone is already airborne"
    tracker.mark_rejected(takeoff_command.id, rejection_reason)
    rejected_record = tracker.get_record(takeoff_command.id)
    
    #assertions
    assert rejected_record is not None
    assert rejected_record.status == CommandStatusEnum.REJECTED
    assert rejected_record.created_at == original_timestamp
    assert rejected_record.started_at is None
    assert rejected_record.finished_at is not None
    assert rejected_record.error_message == rejection_reason
    
    assert rejected_record.command_id == takeoff_command.id
    assert rejected_record.command_type == takeoff_command.command_type
    
    assert rejected_record.finished_at >= rejected_record.created_at


##########test invalid transitions from QUEUED##########
def test_invalid_queued_transitions(tracker, takeoff_command):
    """
    Test 10: Invalid transitions from QUEUED.
    Verify that a QUEUED command cannot transition directly to COMPLETED or FAILED.
    """
    tracker.register(takeoff_command)
    original_record = tracker.get_record(takeoff_command.id)
    
    assert original_record is not None
    assert original_record.status == CommandStatusEnum.QUEUED
    
    with pytest.raises(ValueError):
        tracker.mark_completed(takeoff_command.id)
    
    record_after_completed_attempt = tracker.get_record(takeoff_command.id)
    assert record_after_completed_attempt == original_record
    
    with pytest.raises(ValueError):
        tracker.mark_failed(takeoff_command.id, "Test error")
    
    record_after_failed_attempt = tracker.get_record(takeoff_command.id)
    assert record_after_failed_attempt == original_record


##########test invalid transitions from RUNNING##########
def test_invalid_running_transitions(tracker, takeoff_command):
    """
    Test 11: Invalid transitions from RUNNING.
    Verify that a RUNNING command cannot transition back to RUNNING or to REJECTED.
    """
    tracker.register(takeoff_command)
    tracker.mark_running(takeoff_command.id)
    original_record = tracker.get_record(takeoff_command.id)
    
    assert original_record is not None
    assert original_record.status == CommandStatusEnum.RUNNING
    
    with pytest.raises(ValueError):
        tracker.mark_running(takeoff_command.id)
    
    record_after_running_attempt = tracker.get_record(takeoff_command.id)
    assert record_after_running_attempt == original_record
    
    with pytest.raises(ValueError):
        tracker.mark_rejected(takeoff_command.id, "Test rejection")
    
    record_after_rejected_attempt = tracker.get_record(takeoff_command.id)
    assert record_after_rejected_attempt == original_record


##########test terminal state protection##########
@pytest.mark.parametrize("terminal_status", [
    CommandStatusEnum.COMPLETED,
    CommandStatusEnum.FAILED,
    CommandStatusEnum.REJECTED,
])
@pytest.mark.parametrize("operation", [
    "mark_running",
    "mark_completed",
    "mark_failed",
    "mark_rejected",
])
def test_terminal_state_transitions(tracker, takeoff_command, terminal_status, operation):
    """
    Test 12: Terminal state protection.
    Verify that commands in terminal states (COMPLETED, FAILED, REJECTED) cannot
    transition to any other state. 12 combinations tested via stacked parametrization.
    """
    tracker.register(takeoff_command)
    
    if terminal_status == CommandStatusEnum.COMPLETED:
        tracker.mark_running(takeoff_command.id)
        tracker.mark_completed(takeoff_command.id)
    elif terminal_status == CommandStatusEnum.FAILED:
        tracker.mark_running(takeoff_command.id)
        tracker.mark_failed(takeoff_command.id, "Test failure")
    elif terminal_status == CommandStatusEnum.REJECTED:
        tracker.mark_rejected(takeoff_command.id, "Test rejection")
    
    original_record = tracker.get_record(takeoff_command.id)
    
    assert original_record is not None
    assert original_record.status == terminal_status
    
    with pytest.raises(ValueError):
        if operation == "mark_running":
            tracker.mark_running(takeoff_command.id)
        elif operation == "mark_completed":
            tracker.mark_completed(takeoff_command.id)
        elif operation == "mark_failed":
            tracker.mark_failed(takeoff_command.id, "Test error")
        elif operation == "mark_rejected":
            tracker.mark_rejected(takeoff_command.id, "Test rejection")
    
    record_after_attempt = tracker.get_record(takeoff_command.id)
    assert record_after_attempt == original_record


##########test lifecycle methods with unknown command UUID##########
@pytest.mark.parametrize("operation", [
    "mark_running",
    "mark_completed",
    "mark_failed",
    "mark_rejected",
])
def test_lifecycle_unknown_command(tracker, operation):
    """
    Test 13: Unknown command UUID.
    Verify that all lifecycle methods raise KeyError when called with an unknown UUID.
    Ensure that no spurious record is created by the failed operation.
    """
    unknown_uuid = uuid4()
    
    with pytest.raises(KeyError):
        if operation == "mark_running":
            tracker.mark_running(unknown_uuid)
        elif operation == "mark_completed":
            tracker.mark_completed(unknown_uuid)
        elif operation == "mark_failed":
            tracker.mark_failed(unknown_uuid, "Test error")
        elif operation == "mark_rejected":
            tracker.mark_rejected(unknown_uuid, "Test rejection")
    
    record = tracker.get_record(unknown_uuid)
    assert record is None


##########test tracker instance isolation##########
def test_tracker_instance_isolation(tracker, takeoff_command):
    """
    Test 14: Tracker instance isolation.
    Verify that separate CommandTracker instances maintain independent command records.
    Tests that _records is an instance-level attribute, not class-level.
    """
    second_tracker = CommandTracker()
    
    tracker.register(takeoff_command)
    record_in_first = tracker.get_record(takeoff_command.id)
    record_in_second = second_tracker.get_record(takeoff_command.id)
    
    assert record_in_first is not None
    assert record_in_second is None
    
    second_tracker.register(takeoff_command)
    record_in_second = second_tracker.get_record(takeoff_command.id)
    
    assert record_in_second is not None
    assert record_in_second.status == CommandStatusEnum.QUEUED
    
    tracker.mark_running(takeoff_command.id)
    record_in_first_after = tracker.get_record(takeoff_command.id)
    record_in_second_after = second_tracker.get_record(takeoff_command.id)
    
    assert record_in_first_after.status == CommandStatusEnum.RUNNING
    assert record_in_second_after.status == CommandStatusEnum.QUEUED


##########test independent command lifecycles##########
def test_independent_command_lifecycles(tracker, takeoff_command):
    """
    Test 15: Independent command lifecycles.
    Verify that updating one command's lifecycle does not affect other commands
    in the same tracker.
    """
    land_payload = LandingPayload(landing_speed=1.5)
    land_command = LandCommand(payload=land_payload)
    
    tracker.register(takeoff_command)
    tracker.register(land_command)
    
    land_record_initial = tracker.get_record(land_command.id)
    
    assert land_record_initial is not None
    assert land_record_initial.status == CommandStatusEnum.QUEUED
    
    tracker.mark_running(takeoff_command.id)
    land_record_after_takeoff_running = tracker.get_record(land_command.id)
    
    assert land_record_after_takeoff_running == land_record_initial
    
    tracker.mark_completed(takeoff_command.id)
    land_record_after_takeoff_completed = tracker.get_record(land_command.id)
    
    assert land_record_after_takeoff_completed == land_record_initial
    
    tracker.mark_running(land_command.id)
    takeoff_record_final = tracker.get_record(takeoff_command.id)
    land_record_final = tracker.get_record(land_command.id)
    
    assert takeoff_record_final.status == CommandStatusEnum.COMPLETED
    assert land_record_final.status == CommandStatusEnum.RUNNING
