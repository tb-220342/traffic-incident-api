from enum import Enum


class EventType(str, Enum):
    STOPPED_VEHICLE = "STOPPED_VEHICLE"
    DEBRIS = "DEBRIS"
    CONGESTION = "CONGESTION"
    WRONG_WAY = "WRONG_WAY"
    PEDESTRIAN = "PEDESTRIAN"
    UNKNOWN = "UNKNOWN"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Status(str, Enum):
    NEW = "NEW"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    DISPATCHED = "DISPATCHED"
    RESOLVED = "RESOLVED"
