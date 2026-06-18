from enum import Enum


class InterviewStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    PROCESSING = "PROCESSING"
    ANALYZED = "ANALYZED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class QuestionDifficulty(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class InterviewQuestionStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    ANSWERED = "ANSWERED"
    TIMEOUT = "TIMEOUT"


class InterviewEventType(str, Enum):
    TAB_SWITCH = "TAB_SWITCH"
    WINDOW_BLUR = "WINDOW_BLUR"
    CAMERA_OFF = "CAMERA_OFF"
    MIC_OFF = "MIC_OFF"
    REJOIN = "REJOIN"
    QUESTION_TIMEOUT = "QUESTION_TIMEOUT"
    INTERVIEW_STARTED = "INTERVIEW_STARTED"
    INTERVIEW_COMPLETED = "INTERVIEW_COMPLETED"


class RecordingStatus(str, Enum):
    PENDING = "PENDING"
    RECORDING = "RECORDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ReadingRisk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"