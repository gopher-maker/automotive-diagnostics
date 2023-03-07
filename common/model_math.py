"""Math utilities for modeling."""

import math


def park_transform(phase_a, phase_b, phase_c, theta):
  """Computes the d-q space equivalent of a 3-phase quantity.
  Args:
    phase_a: float representing 'A phase' of a 3-phase quantity.
    phase_b: float representing 'B phase' of a 3-phase quantity.
    phase_c: float representing 'C phase' of a 3-phase quantity.
  Returns:
    d_component: float representing 'direct' component of 3-phase quantity.
    q_component: float representing 'quadrature' component of 3-phase quantity.
  """
  d_component = (2 / 3) * (
    phase_a * math.cos(theta) +
    phase_b * math.cos(theta - (2 * math.pi / 3)) +
    phase_c * math.cos(theta + (2 * math.pi / 3))
  )

  q_component = (2 / 3) * (
    - phase_a * math.sin(theta)
    - phase_b * math.sin(theta - (2 * math.pi / 3))
    - phase_c * math.sin(theta + (2 * math.pi / 3))
  )

  return d_component, q_component
