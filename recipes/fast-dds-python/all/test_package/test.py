"""Smoke test for the fastdds python bindings: exercises the SWIG module
beyond import, without opening any network resources (no participant is
created)."""

import fastdds

factory = fastdds.DomainParticipantFactory.get_instance()
assert factory is not None

qos = fastdds.DomainParticipantQos()
assert qos.name() is not None

print("fastdds python bindings OK")
