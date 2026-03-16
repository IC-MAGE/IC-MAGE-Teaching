from m02_tx_integrator.parameters import MaterialParameters, SmallStrainParameters
from m02_tx_integrator.test_conditions import TestConditions


def nevada_sand_original() -> tuple[MaterialParameters, SmallStrainParameters]:
    material = MaterialParameters(
        ecsref=0.887,
        l=0.079,
        csi=0.250,
        pref=100.0,
        mcs=1.2872,
        k1=2.4,
        k2=0.0,
        l1=3.7,
        l2=0.0,
    )
    stiffness = SmallStrainParameters(
        g0=51860.0,
        mg=0.5,
        a0=1.09e-4,
        b=1.13,
        rgmin=0.1,
        pr=0.2,
    )
    return material, stiffness


def nevada_sand_dr_based() -> tuple[MaterialParameters, SmallStrainParameters]:
    material = MaterialParameters(
        ecsref=0.774,
        l=0.0,
        csi=1.0,
        pref=100.0,
        mcs=1.2872,
        k1=1.8,
        k2=-0.3,
        l1=2.4,
        l2=-0.35,
    )
    stiffness = SmallStrainParameters(
        g0=51860.0,
        mg=0.5,
        a0=1.09e-4,
        b=1.13,
        rgmin=0.1,
        pr=0.2,
    )
    return material, stiffness


def reference_tests() -> list[TestConditions]:
    return [
        TestConditions(label="CIDC40-107", e0=0.728, p0=40.0, q0=0.0),
        TestConditions(label="CIDC40-100", e0=0.726, p0=80.0, q0=0.0),
        TestConditions(label="CIDC40-106", e0=0.718, p0=160.0, q0=0.0),
        TestConditions(label="CIDC60-82", e0=0.657, p0=40.0, q0=0.0),
        TestConditions(label="CIDC60-75", e0=0.652, p0=80.0, q0=0.0),
        TestConditions(label="CIDC60-81", e0=0.651, p0=160.0, q0=0.0),
        TestConditions(label="CADC40-108", e0=0.723, p0=80.0, q0=44.0),
        TestConditions(label="CADC60-70", e0=0.653, p0=80.0, q0=44.0),
    ]