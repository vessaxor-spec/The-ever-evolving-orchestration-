"""Legacy deterministic calibration import/CLI; implementation is in adapters.evaluation.verifier_calibration."""

from .adapters.evaluation.verifier_calibration import *  # noqa: F401,F403
from .adapters.evaluation.verifier_calibration import (
    _required_text,
    _required_offset_datetime,
    _required_bool,
    _required_positive_int,
    _optional_non_negative_int,
    _optional_non_negative_float,
    _conditional_rate,
    _validate_observation_set,
    _percentile,
)


if __name__ == "__main__":
    raise SystemExit(main())
