from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class IntegrationResult:
    label: str
    eax: list[float]
    erad: list[float]
    evol: list[float]
    ed: list[float]
    p: list[float]
    q: list[float]
    vr: list[float]
    pvr: list[float]
    psi: list[float]
    mtxc: list[float]
    mdil: list[float]
    fy: list[float]
    gtan: list[float]
    ktan: list[float]
    ppeak: float
    qpeak: float
    pcs: float
    qcs: float

    def to_dataframe(self, clean: bool = False) -> pd.DataFrame:
        if clean:
            return pd.DataFrame(
                {
                    "eax_percent": self.eax,
                    "evol_percent": self.evol,
                    "p": self.p,
                    "q": self.q,
                    "void_ratio": self.vr,
                    "plastic_void_ratio": self.pvr,
                    "ed": self.ed,
                    "psi": self.psi,
                    "mtxc": self.mtxc,
                    "mdil": self.mdil,
                    "fy": self.fy,
                    "gtan": self.gtan,
                    "ktan": self.ktan,
                }
            )

        dataframe = pd.DataFrame(
            columns=["eax0%", "evol%", "eax1%", "q0", "p0", "q1", "p1", "e", "Ed0", "q2", "Ed1", "Gtan"]
        )
        dataframe["eax0%"] = self.eax
        dataframe["evol%"] = self.evol
        dataframe["eax1%"] = self.eax
        dataframe["q0"] = self.q
        dataframe["p0"] = self.p
        dataframe["q1"] = self.q
        dataframe["p1"] = self.p
        dataframe["e"] = self.vr
        dataframe["Ed0"] = self.ed
        dataframe["q2"] = self.q
        dataframe["Ed1"] = self.ed
        dataframe["Gtan"] = self.gtan
        return dataframe