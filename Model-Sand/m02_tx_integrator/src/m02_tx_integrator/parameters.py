from dataclasses import dataclass


@dataclass(frozen=True)
class MaterialParameters:
    ecsref: float
    l: float
    csi: float
    pref: float
    mcs: float
    k1: float
    k2: float
    l1: float
    l2: float


@dataclass(frozen=True)
class SmallStrainParameters:
    g0: float
    mg: float
    a0: float
    b: float
    rgmin: float
    pr: float