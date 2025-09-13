# Domain Knowledge References

Initial list (user-provided). Status values: pending, downloaded, paywalled, error, duplicate.

| Link | DOI/Identifier | Status | Notes |
|------|----------------|--------|-------|
| https://www.sciencedirect.com/science/article/pii/S0933365725000892?via%3Dihub | S0933365725000892 | downloaded | PDF present; converted as `1-s2.0-S0933365725000892-main.converted.md` |
| https://link.springer.com/chapter/10.1007/978-3-031-06388-6_14 | 10.1007/978-3-031-06388-6_14 | downloaded | PDF present; converted as `978-3-031-06388-6_14.converted.md` |
| https://link.springer.com/chapter/10.1007/978-3-031-06388-6_14 | 10.1007/978-3-031-06388-6_14 | duplicate | Duplicate entry from list |
| https://ieeexplore.ieee.org/document/9460947 | IEEE 9460947 | access_blocked | IEEE page returned access rejection; requires institutional login |
| https://link.springer.com/chapter/10.1007/978-3-030-78089-0_12 | 10.1007/978-3-030-78089-0_12 | downloaded | PDF present; converted as `978-3-030-78089-0_12.converted.md` |
| https://link.springer.com/chapter/10.1007/978-3-030-17462-0_16 | 10.1007/978-3-030-17462-0_16 | downloaded | PDF present; converted as `978-3-030-17462-0_16.converted.md` |

| https://arxiv.org/abs/2002.06177 | arXiv:2002.06177 | downloaded | PDF `marcus_2020_arxiv_2002.06177.pdf` (pending conversion) |
| https://arxiv.org/abs/1909.01310 | arXiv:1909.01310 | downloaded | PDF `bengio_2019_arxiv_1909.01310.pdf` (pending conversion) |
| https://www.fda.gov/media/145022/download | FDA 2021 SaMD Action Plan | downloaded | PDF `fda_2021_AIML_SaMD_Action_Plan.pdf` (public document) |
| https://link.springer.com/chapter/10.1007/BFb0025774 | 10.1007/BFb0025774 | paywalled | Clarke & Emerson 1981 LNCS 131 chapter (no PDF locally) |
| https://link.springer.com/chapter/10.1007/3-540-11494-7_22 | 10.1007/3-540-11494-7_22 | paywalled | Queille & Sifakis 1982 chapter (no PDF locally) |
| https://dl.acm.org/doi/10.1145/360018.360022 | 10.1145/360018.360022 | paywalled | Newell & Simon 1976 CACM (no PDF) |
| https://doi.org/10.1109/TIT.1956.1056797 | 10.1109/TIT.1956.1056797 | paywalled | Newell & Simon 1956 IRE Trans. IT (no PDF) |
| https://doi.org/10.1016/j.tcs.2014.07.014 | 10.1016/j.tcs.2014.07.014 | paywalled | Ciancia et al. 2014 TCS (no PDF) |
| https://link.springer.com/chapter/10.1007/978-3-031-75387-9_13 | 10.1007/978-3-031-75387-9_13 | pending | Belmonte et al. 2024 (add PDF if license permits) |
| https://github.com/avian2/VoxLogicA | VoxLogicA repo | software | Software project (cite as tool; no PDF) |
| https://mitpress.mit.edu/9780262680530/parallel-distributed-processing/ | Rumelhart et al. 1986 | book | PDP Volume 1 (no PDF added) |
| https://www.routledge.com/Duality-of-the-Mind-A-Bottom-Up-Approach-Toward-Cognition/Sun/p/book/9780805844617 | Sun 2002 | book | Duality of the Mind (no PDF) |
| https://www.penguinrandomhouse.com/books/566677/human-compatible-by-stuart-russell/ | Russell 2019 | book | Human Compatible (no PDF) |
| https://www.sciencedirect.com/science/article/pii/S0933365725000892?via%3Dihub |  S0933365725000892 | duplicate? | Already listed above; keep single downloaded entry |

## Lecture 01 – Core Reference Subset (Minimal)

The following 9 entries form the intentionally minimal, high‑yield set aligned with the Lecture 01 narrative (model checking foundations, spatial/logical methods in imaging, hybrid & neuro‑symbolic motivation, alignment/safety, and regulatory context). Each identifier maps to the full table above; no duplication of metadata/PDF storage occurs here.

| Identifier | Topic | Role in Lecture 01 |
|------------|-------|--------------------|
| 10.1007/BFb0025774 | Model checking | Foundational branching‑time temporal logic & state‑space verification paradigm. |
| 10.1016/j.tcs.2014.07.014 | Spatial model checking | Introduces spatial logics leveraged for imaging (conceptual bridge to VoxLogicA). |
| 10.1007/978-3-031-75387-9_13 | Hybrid AI in imaging | Recent application of spatial model checking within hybrid imaging workflows. |
| arXiv:2002.06177 | Robustness critique | Highlights structural limits of deep models motivating symbolic augmentation. |
| arXiv:1909.01310 | System 1→2 shift | Proposes inductive biases for higher‑level (quasi‑symbolic) reasoning in deep learning. |
| Sun 2002 | Dual‑layer cognition | Theoretical basis for coexistence of implicit (subsymbolic) and explicit (symbolic) processes. |
| Russell 2019 | Alignment & control | Motivates explicit models for safety, corrigibility, and governance. |
| FDA 2021 SaMD Action Plan | Regulation | Provides real‑world safety/regulatory driver for explainable, auditable pipelines. |
| VoxLogicA repo | Tooling | Concrete implementation of spatial model checking supporting hybrid workflows. |

Selection principles: (i) Eliminate redundancy among overlapping conceptual critiques; (ii) Prefer one authoritative exemplar per conceptual slot; (iii) Balance historical foundations with current applied and governance perspectives.

## Comprehensive Bibliography File

A consolidated BibTeX file `full_course_references.bib` at the repository root aggregates foundational, spatial logic, hybrid AI, cognitive architecture, robustness, alignment, regulatory, and tooling references. It is injected into the lecture notes via the `<!-- INSERT-BIB full_course_references.bib -->` directive and rendered directly into markdown without intermediate files.

