import math
from collections.abc import Iterable

from m02_tx_integrator.parameters import MaterialParameters, SmallStrainParameters
from m02_tx_integrator.results import IntegrationResult
from m02_tx_integrator.test_conditions import TestConditions


class ConvergenceError(RuntimeError):
    pass


class TXCIntegrator:
    def __init__(self, material: MaterialParameters, stiffness: SmallStrainParameters):
        self.material = material
        self.stiffness = stiffness

    def run(
        self,
        test: TestConditions,
        n_elastic_steps: int = 1000,
        n_plastic_steps: int = 1000,
        peak_tolerance: float = 1e-10,
        max_peak_iterations: int = 100,
    ) -> IntegrationResult:
        if n_elastic_steps <= 0:
            raise ValueError("n_elastic_steps must be positive")
        if n_plastic_steps <= 0:
            raise ValueError("n_plastic_steps must be positive")
        if max_peak_iterations <= 0:
            raise ValueError("max_peak_iterations must be positive")

        ppeak, qpeak = self._compute_peak_conditions(
            test=test,
            peak_tolerance=peak_tolerance,
            max_peak_iterations=max_peak_iterations,
        )
        pcs, qcs = self._compute_critical_state(test)

        eax = [0.0]
        erad = [0.0]
        evol = [0.0]
        ed = [0.0]
        p = [test.p0]
        q = [test.q0]
        vr = [test.e0]
        pvr = [test.e0]

        psi0 = self._state_parameter(pvr[0], test.p0)
        psi = [psi0]

        mtxc = [self._txc_slope(psi0)]
        mdil = [self.material.mcs - self.material.l1 * ((-psi0) ** (self.material.l2 + 1.0))]

        gt = self._shear_stiffness(test.p0, ed[0])
        gtan = [gt]
        ktan = [self._bulk_stiffness(gt)]
        fy = [test.q0 - test.p0 * mtxc[0]]

        self._integrate_elastic(
            test=test,
            ppeak=ppeak,
            n_steps=n_elastic_steps,
            eax=eax,
            erad=erad,
            evol=evol,
            ed=ed,
            p=p,
            q=q,
            vr=vr,
            pvr=pvr,
            psi=psi,
            mtxc=mtxc,
            mdil=mdil,
            fy=fy,
            gtan=gtan,
            ktan=ktan,
        )
        self._integrate_plastic(
            test=test,
            ppeak=ppeak,
            pcs=pcs,
            n_steps=n_plastic_steps,
            eax=eax,
            erad=erad,
            evol=evol,
            ed=ed,
            p=p,
            q=q,
            vr=vr,
            pvr=pvr,
            psi=psi,
            mtxc=mtxc,
            mdil=mdil,
            fy=fy,
            gtan=gtan,
            ktan=ktan,
        )

        eax_percent = [value * 100.0 for value in eax]
        evol_percent = [value * 100.0 for value in evol]

        return IntegrationResult(
            label=test.label,
            eax=eax_percent,
            erad=erad,
            evol=evol_percent,
            ed=ed,
            p=p,
            q=q,
            vr=vr,
            pvr=pvr,
            psi=psi,
            mtxc=mtxc,
            mdil=mdil,
            fy=fy,
            gtan=gtan,
            ktan=ktan,
            ppeak=ppeak,
            qpeak=qpeak,
            pcs=pcs,
            qcs=qcs,
        )

    def run_batch(
        self,
        tests: Iterable[TestConditions],
        n_elastic_steps: int = 1000,
        n_plastic_steps: int = 1000,
        peak_tolerance: float = 1e-10,
        max_peak_iterations: int = 100,
    ) -> list[IntegrationResult]:
        return [
            self.run(
                test=test,
                n_elastic_steps=n_elastic_steps,
                n_plastic_steps=n_plastic_steps,
                peak_tolerance=peak_tolerance,
                max_peak_iterations=max_peak_iterations,
            )
            for test in tests
        ]

    def _compute_peak_conditions(
        self,
        test: TestConditions,
        peak_tolerance: float,
        max_peak_iterations: int,
    ) -> tuple[float, float]:
        psi0 = self._state_parameter(test.e0, test.p0)
        mt = self._txc_slope(psi0)
        ppeak = test.p0
        last_delta = float("inf")

        for _ in range(max_peak_iterations):
            next_ppeak = (
                ppeak / 3.0 * self.material.mcs
                + self.material.k1
                / 3.0
                * ppeak
                * (self.material.ecsref - self.material.l * (ppeak / self.material.pref) ** self.material.csi - test.e0)
                ** (self.material.k2 + 1.0)
                + test.p0
                - test.q0 / 3.0
            )
            last_delta = abs(next_ppeak - ppeak)
            ppeak = next_ppeak

        if last_delta > peak_tolerance:
            raise ConvergenceError(
                f"Peak condition solver did not converge for test '{test.label}' within {max_peak_iterations} iterations"
            )

        qpeak = ppeak * mt
        return ppeak, qpeak

    def _compute_critical_state(self, test: TestConditions) -> tuple[float, float]:
        pcs = (3.0 * test.p0 - test.q0) / (3.0 - self.material.mcs)
        qcs = pcs * self.material.mcs
        return pcs, qcs

    def _integrate_elastic(
        self,
        test: TestConditions,
        ppeak: float,
        n_steps: int,
        eax: list[float],
        erad: list[float],
        evol: list[float],
        ed: list[float],
        p: list[float],
        q: list[float],
        vr: list[float],
        pvr: list[float],
        psi: list[float],
        mtxc: list[float],
        mdil: list[float],
        fy: list[float],
        gtan: list[float],
        ktan: list[float],
    ) -> None:
        pstep = (ppeak - test.p0) / n_steps
        qstep = 3.0 * pstep

        for _ in range(n_steps):
            devole = pstep / ktan[-1]
            dede = qstep / (math.sqrt(3.0) * gtan[-1])

            evol.append(evol[-1] + devole)
            ed.append(ed[-1] + dede)
            eax.append(eax[-1] + devole / 3.0 + dede / math.sqrt(3.0))
            erad.append(erad[-1] + devole / 3.0 + dede / (2.0 * math.sqrt(3.0)))
            p.append(p[-1] + pstep)
            q.append(q[-1] + qstep)
            vr.append(vr[-1] - (1.0 + test.e0) * devole)
            pvr.append(pvr[-1])

            next_psi = self._state_parameter(pvr[-1], p[-1])
            psi.append(next_psi)
            next_gtan = self._shear_stiffness(p[-1], ed[-1])
            gtan.append(next_gtan)
            ktan.append(self._bulk_stiffness(next_gtan))
            mtxc.append(self._txc_slope(next_psi))
            mdil.append(self.material.l1 * ((-next_psi) ** (self.material.l2 + 1.0)))
            fy.append(q[-1] - p[-1] * mtxc[-1])

    def _integrate_plastic(
        self,
        test: TestConditions,
        ppeak: float,
        pcs: float,
        n_steps: int,
        eax: list[float],
        erad: list[float],
        evol: list[float],
        ed: list[float],
        p: list[float],
        q: list[float],
        vr: list[float],
        pvr: list[float],
        psi: list[float],
        mtxc: list[float],
        mdil: list[float],
        fy: list[float],
        gtan: list[float],
        ktan: list[float],
    ) -> None:
        pstep = (pcs - ppeak) / n_steps
        qstep = 3.0 * pstep

        for _ in range(n_steps):
            devole = pstep / ktan[-1]
            dede = qstep / (math.sqrt(3.0) * gtan[-1])

            dfdp = (
                -mtxc[-1]
                + p[-1]
                * self.material.k1
                * (self.material.k2 + 1.0)
                * ((-psi[-1]) ** self.material.k2)
                * (self.material.l * self.material.csi / self.material.pref)
                * ((p[-1] / self.material.pref) ** (self.material.csi - 1.0))
            )
            dfdq = 1.0
            dpdp = -mdil[-1]
            dpdq = 1.0
            dfdep = p[-1] * self.material.k1 * (self.material.k2 + 1.0) * ((-psi[-1]) ** self.material.k2)
            qval = dfdp * dpdp * ktan[-1] + 3.0 * dfdq * dpdq * gtan[-1]
            rval = qval + dfdep * (1.0 + test.e0) * dpdp
            d11 = ktan[-1] - ktan[-1] * ktan[-1] * dfdp * dpdp / rval
            d12 = -3.0 * ktan[-1] * gtan[-1] * dfdq * dpdp / rval
            d21 = -3.0 * ktan[-1] * gtan[-1] * dfdp * dpdq / rval
            d22 = 3.0 * gtan[-1] - (9.0 * gtan[-1] * gtan[-1]) * dfdq * dpdq / rval
            detd = d11 * d22 - d12 * d21
            di11 = d22 / detd
            di12 = -d12 / detd
            di21 = -d21 / detd
            di22 = d11 / detd
            devol = di11 * pstep + di12 * qstep
            ded = math.sqrt(3.0) * (di21 * pstep + di22 * qstep)
            devolp = devol - devole
            dpvr = -(1.0 + test.e0) * devolp

            evol.append(evol[-1] + devol)
            ed.append(ed[-1] + ded)
            eax.append(eax[-1] + devol / 3.0 + ded / math.sqrt(3.0))
            erad.append(erad[-1] + devol / 3.0 + ded / (2.0 * math.sqrt(3.0)))
            p.append(p[-1] + pstep)
            q.append(q[-1] + qstep)
            vr.append(vr[-1] - (1.0 + test.e0) * devol)
            pvr.append(pvr[-1] + dpvr)

            next_psi = self._state_parameter(pvr[-1], p[-1])
            if next_psi > -1e-6:
                next_psi = -1e-6

            psi.append(next_psi)
            next_gtan = self._shear_stiffness(p[-1], ed[-1])
            gtan.append(next_gtan)
            ktan.append(self._bulk_stiffness(next_gtan))
            mtxc.append(self._txc_slope(next_psi))
            mdil.append(self.material.l1 * ((-next_psi) ** (self.material.l2 + 1.0)))
            fy.append(q[-1] - p[-1] * mtxc[-1])

    def _state_parameter(self, void_ratio: float, mean_stress: float) -> float:
        return void_ratio - (
            self.material.ecsref - self.material.l * (mean_stress / self.material.pref) ** self.material.csi
        )

    def _txc_slope(self, psi: float) -> float:
        return self.material.mcs + self.material.k1 * ((-psi) ** (self.material.k2 + 1.0))

    def _shear_stiffness(self, mean_stress: float, deviatoric_strain: float) -> float:
        return self.stiffness.g0 * ((mean_stress / self.material.pref) ** self.stiffness.mg) * (
            self.stiffness.rgmin
            + (1.0 - self.stiffness.rgmin) / (1.0 + (deviatoric_strain / self.stiffness.a0) ** self.stiffness.b)
        )

    def _bulk_stiffness(self, shear_stiffness: float) -> float:
        return 2.0 * shear_stiffness * (1.0 + self.stiffness.pr) / (3.0 * (1.0 - 2.0 * self.stiffness.pr))