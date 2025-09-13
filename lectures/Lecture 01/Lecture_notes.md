# Lecture 1: Formal and Hybrid Methods for Medical Imaging

**Course:** Formal and Hybrid Methods for Medical Imaging  
**Date:** September 10, 2025  
**Instructor:** Vincenzo Ciancia

## Who We Are

We are researchers from two complementary groups at ISTI‑CNR working at the intersection of formal methods, signal processing and medical imaging: FMTLAB (Formal Methods and Tools) and SILAB (Signal and Image Laboratory). Our teams combine expertise in executable formal specifications, spatial logics and model checking, ethics in AI, machine learning, with practical experience in imaging, radiomics and machine learning. The goal is to develop reproducible, interpretable, and verifiable pipelines for medical image analysis that are suitable for research and clinical translation.

### Key people (in the course):

- Vincenzo Ciancia — Researcher, ISTI‑CNR (FMTLAB). Research interests include formal methods, model checking and spatial logics applied to image analysis and computational verification. Vincenzo works on spatial logics and spatial model checking, declarative image specification and tools that connect logical assertions to imaging pipelines.

- Mieke Massink — Researcher, ISTI‑CNR. Focuses on model checking, formal methods and quantitative verification; other half of the core group working on spatial logics, model checking and its application to imaging.

- Manuela Imbriani — Researcher / Medical Physicist, ISTI‑CNR (collaborating with clinical partners). Works on imaging physics and the applied aspects of medical image analysis; will be joining IEO Milano in January 2026.

- Sara Colantonio — Researcher, SILAB (ISTI‑CNR). Specialises in signal analysis and AI methods for medical imaging and healthcare applications.

- Danila Germanese — Researcher, SILAB (ISTI‑CNR). Works on radiomics, feature engineering and applied machine learning for imaging workflows.

### What we do

Our work spans from foundational research (spatial formalisms and verification algorithms) to applied pipelines (segmentation, radiomics, hybrid neural‑symbolic workflows). We develop open tools, reproducible experiments, and teaching materials that make formal verification methods accessible to imaging practitioners and students.

For more details and up‑to‑date profiles, see the ISTI‑CNR group pages and individual webpages linked from the course domain knowledge folder.

## The course

*This course stems from the need to bridge a specific gap between recent research, and university-level education, driven by major improvements in Artificial Intelligence, particularly deep learning. We aim to introduce symbolic and hybrid methods to students of the Informatics for Digital Health program, aligning with broader efforts toward trustworthy, explainable, accountable, and auditable AI in sensitive domains. In the field of Medical Image Analysis, model checking has shown promising results in applying logical methods to Computer Vision, and this will be a central theme of the course, while departing from the symbolic/deductive AI tradition.*

<!-- SLIDE -->
Bridging Research and Education in Medical Image Analysis

- Recent advances in AI, especially deep learning, have created a gap between research and university curricula.
- This course introduces symbolic and hybrid methods to Informatics for Digital Health students.
- Focus: trustworthy, explainable, accountable, and auditable AI in sensitive domains.
- Model checking applies logical methods to Computer Vision—central to the course, moving beyond traditional symbolic/deductive AI.
<!-- NOTES -->

*While the methods presented here represent only a small part of the current research frontier, there is not yet a well-established methodology in this area. Thus, it is essential to foster the development and dissemination of these approaches among new generations which will be the ones shaping the actual implementation plan for digital health in age of Artificial Intelligence, and must possess all the needed instruments to critically evaluate and apply these methodologies.*

<!-- SLIDE -->
**Emerging Methodologies in Digital Health AI**

- Current symbolic and hybrid methods represent a small fraction of ongoing research.
- No universally established methodology exists yet in this area.
- Fostering development and dissemination is crucial for future professionals.
- New generations will shape digital health implementation and must be equipped to critically evaluate and apply these approaches.

<!-- NOTES -->


## The course notes

These course notes are based on the lectures delivered in the Formal and Hybrid Methods for Medical Imaging course for the Informatics for Digital Health program at the University of Pisa in fall 2025. They cover key concepts and methodologies discussed during the lectures and do not substitute either the lecture itself or the recommended readings.

The production of the course material **has been aided by AI agents**, but all inputs and outputs have been supervised, curated, and manually edited by the author—reflecting a human‑in‑the‑loop approach appropriate for safety‑critical contexts. The full process is documented in the public git history: https://github.com/vincenzoml/UNIPI-MIM

## Formal methods for medical imaging

This course focuses on a selection of topics positioned between classical programming and AI. For the symbolic part, we study *model checking*. This approach departs from the traditional deductive view of symbolic AI (theorem proving, logic programming) and instead emphasizes the pragmatic use of executable domain knowledge. Properties of a system (or, here, medical images and their derived feature structures) are specified formally and then automatically verified against concrete models using efficient algorithms. This paradigm has proven effective in computer vision applications only relatively recently.


**Deductive tradition in symbolic AI:**  
The deductive tradition in symbolic AI dates back to the earliest logic‑inspired systems. Early programs such as the Logic Theorist and later the emergence of logic programming focused on deriving conclusions from axioms using inference rules, automated reasoning, and theorem proving. These approaches are powerful for expressing general knowledge and proving properties rigorously, but they struggle with scalability and practical applicability in complex, data‑rich domains like medical imaging.


**Model checking as a pragmatic alternative:**  
Model checking provides automated verification of formally specified properties over finite models via systematic state exploration. Rather than attempting fully general theorem proving, it algorithmically determines whether a model satisfies given temporal/spatial properties. Initially successful in hardware and protocol verification, it now extends to imaging workflows where executable spatial or structural knowledge can be encoded and checked efficiently. (Editorial placeholders removed; original citation notes resolved.)

{EXPAND: insert definitions "automated verification" "finite mdeols" "systematic state exploration" "temporal/spatial properties". Explain the role of modal logic. Explain what is a modal formula. Make examples. Explain the problem of combinatorial explosion in parallel systems. 

Mention the various milestones in model checking, the pionieers, the major active researchers and groups, and the main tools.}

{Make a simple example of temporal model checking}

{Make a simple example of spatial model checking, explain the role of spatial logics, emphasize the strong EU tradition in spatial logics, mention the main researchers and groups, and the main tools.}

By focusing on model checking, the course emphasizes a methodology that is both expressive and practical, enabling specification and automated verification of complex properties in medical images without reliance on full deductive proof frameworks. This reflects a broader trend toward tools that balance rigor, usability, and scalability.

Despite their potential, symbolic and hybrid methods are still emerging in medical imaging. Challenges include integrating heterogeneous data sources, developing scalable algorithms, and creating user‑friendly tools for clinicians. Interdisciplinary collaboration is essential to bridge research and applied clinical deployment.

Fostering knowledge and skills in these areas supports improved patient outcomes, advances research, and prepares future professionals to navigate an increasingly digital healthcare landscape.

## Multidisciplinary, seminar-style structure of the course

This course is intentionally multidisciplinary and delivered in a seminar style: multiple experts contribute lectures, discussions, and hands‑on sessions. You will encounter complementary viewpoints spanning methodology, imaging practice, data handling, formal reasoning, spatial logics, radiomics, and hybrid AI engineering. Rotating instructors focus on domain strengths, grounding material in current research questions and real‑world constraints.

### Complementary thematic threads (as reflected in the schedule)

- Foundations of paradigms: symbolic, formal, subsymbolic, and hybrid approaches; positioning model checking among verification techniques

- Ethics and human‑centric AI: responsible use, transparency, professional considerations

- Medical imaging physics & modalities: CT / MRI acquisition principles and reconstruction pipelines

- Image reconstruction & enhancement: algorithms, low‑dose strategies, artifact reduction, links to deep learning

- Data engineering & preparation: pipeline design, dataset creation, curation, governance

- Pre-processing & segmentation fundamentals: from theoretical principles to practical brain imaging segmentation

- Spatial logics & declarative image analysis: model checking, VoxLogicA, expressive spatial property specification

- Advanced declarative workflows: performance optimisation, tooling, case study–driven refinement

- Radiomics & machine learning: feature extraction, pipelines, evaluation protocols, model cards, ethical implications

- Performance and constraints: metrics beyond accuracy (geometry, distance, reachability), pitfalls and failure modes

- Hybrid AI integration: combining spatial logic specifications with neural architectures (e.g. nnU-Net), determinism and reproducibility concerns

- Case studies: brain lesion segmentation, brain tissue identification, comparative methodological insights

These threads are interleaved: conceptual lectures introduce formal or methodological tools, followed by practical hands-on sessions that expose implementation subtleties, optimisation trade-offs, and ethical or professional implications. You are encouraged to treat the material not as a linear textbook narrative but as a mosaic of interoperable techniques that can be recombined when designing robust, explainable, and clinically relevant imaging workflows.

## Leading theme

## The Image Processing Pipeline

The topics of this course fit into a mental model related to the typical image processing pipeline, as shown in the following diagram.


```{mermaid}
%%{init: {
    "theme": "neutral",
    "flowchart": { "htmlLabels": true, "useMaxWidth": false },
    "themeVariables": {
                "fontSize": "24px",
                "fontFamily": "Helvetica Neue, Arial, sans-serif",
                "fontWeight": "700",
                "padding": 40px             
    },
        "themeCSS": ".label div{display:flex;align-items:center;justify-content:center;padding:25px 25px 25px 25px !important;line-height:1.1;} .node rect{stroke-width:4px;}"
} }%%
flowchart LR
    A["Data Acquisition"] --> B["Preprocessing"]
    B --> C["Segmentation"]
    C --> D["Feature Extraction"]
    D --> E["Analysis"]
    E --> F["Structure Classification"]
```

## The schedule revisited

### Data Acquisition and Preprocessing

**Acquisition**
- Week 2: Imaging modalities (MRI, CT); reconstruction basics; modality characteristics; early DL applications in reconstruction.

**Preprocessing**
- Week 3: Principles of image pre‑processing; dataset creation & curation.

### Segmentation
- Week 4: Introduction to medical image segmentation; hands‑on background removal + brain segmentation.

- Week 5: Spatial logics, model checking, VoxLogicA; hands‑on declarative analysis.

- Week 8: Advanced declarative analysis, optimisation (voxlogica.py), case studies (performance tuning).

### Feature Extraction
- Week 9: Radiomics concepts; ethics & professional considerations; model cards; hands‑on radiomics pipelines & evaluation.

### Analysis & Structure Classification
- Week 10: Performance metrics (geometry, distance, reachability); constraints & pitfalls; hybrid workflows combining VoxLogicA with neural models (nnU‑Net); determinism & reproducibility concerns.

### Case Studies & Hybrid Practice (Pipeline Context: Postprocessing + Applied Hybrid Workflows)
- Week 11: Case studies (brain lesion segmentation; brain tissue identification); practical hybrid workflows on provided datasets.

## Symbolic and Hybrid AI
### Introduction

Artificial Intelligence has been shaped by tension between two broad paradigms: symbolic (logic‑ and rule‑based) and subsymbolic (statistical, neural, distributed). Each reflects distinct assumptions about representation and computation. The contemporary push toward hybrid AI—integrating structured knowledge, formal reasoning, and data‑driven learning—responds to the limits of each paradigm in isolation. In medical imaging, where interpretability, robustness, data heterogeneity, and safety are paramount, this integrative turn is especially compelling.

### Roots of the Symbolic Paradigm

The origins of symbolic AI trace back to the **1950s and 1960s**, during the so-called *first AI summer*. Pioneering systems like the *Logic Theorist* and *General Problem Solver* demonstrated that reasoning processes could be captured in computational form. Research at that time focused on **knowledge representation**, heuristics, and automated theorem proving, reflecting a strong optimism about the prospects of human-level intelligence through symbolic reasoning. 

This foundational work framed intelligent behaviour as heuristic search through structured problem spaces governed by production rules. Symbol systems promised transparency, compositionality, and explainability—qualities attractive for domains requiring traceable decision paths. Logic programming and automated theorem proving exemplified declarative specification of domain knowledge.

However, this optimism was tempered by subsequent **AI winters**, as limitations became apparent. Symbolic systems proved brittle: they often failed when faced with incomplete knowledge, ambiguity, or situations outside their carefully designed domains. Knowledge acquisition was another bottleneck, since encoding expertise into formal symbolic rules was time-consuming and error-prone.

The **late 1970s and 1980s** saw the rise of **expert systems**, which encoded specialist knowledge into large rule bases and enjoyed considerable commercial success. These systems demonstrated practical value in fields such as medicine (e.g. MYCIN), engineering, and finance, although their limitations again surfaced when scaling beyond narrow domains.

{cite major authors of the time and mention their subsequent career paths; add years for major milestones or events}

In Computer Science, a *brittle* system is fragile: it works well under expected conditions but fails suddenly or catastrophically when it goes beyond its ideal scenario (a typical example being the expert systems of the 1980s, which were very rigid when facing exceptions).

{Explain what is: 1. logic theorist 2. general problem solver 3. logic programming 4. automated theorem proving. }

{How did it proceed? Fill the missing historical gap between the expert systems and the subsymbolic}


### Rise of the Subsymbolic / Connectionist Paradigm

The reaction to symbolic brittleness catalysed interest in distributed representations. Parallel distributed processing demonstrated how networks learn statistical regularities instead of relying on hand‑crafted rules. Meaning emerges from activation patterns and weight configurations. Such systems excel at perceptual tasks (classification, segmentation, pattern completion) where symbolic systems struggled. Challenges remained: limited transparency, compositional generalisation, data efficiency, and handling of multi‑step reasoning or variable binding.

{Expand: insert examples of key models, e.g. Perceptron, Backpropagation, CNNs, RNNs, Transformers, main proponents of the time, and their career paths. }

{Insert a section: the advent of deep learning; make it 3-4 paragraphs, mention major breakthroughs, architectures, and their impact on AI research and applications. Connect to the advent of GPU computing, large datasets, and the rise of transformer architectures.}

### Contemporary Critiques and Extensions

Modern deep learning has dramatically advanced subsymbolic performance while exposing limits: brittleness, shallow abstraction, difficulty with causal inference and flexible transfer. Emerging research emphasizes inductive biases (modularity, attention, sparsity) to promote compositional, higher‑level reasoning.

{Expand: for each of the above mentioned issues one-two paragraph with clear explanations}

Dual‑layer perspectives emphasise that robust intelligence integrates implicit (procedural, distributed) and explicit (declarative, rule‑based) knowledge. This resonates with imaging workflows where low‑level feature extraction must interface with higher‑level anatomical or clinical concepts.

Concerns about alignment and control motivate explicit modelling of preferences, uncertainty, and consequences. Embedding structured models alongside learned components supports safer, auditable decision pipelines.

{These notes are for university students. Please avoid jargon and explain all technical terms.}

### Structural Limitations Driving Hybridization

| Limitation | Symbolic Systems | Subsymbolic Systems | Hybrid Opportunity |
|------------|-----------------|---------------------|--------------------|
| Perception | Fragile; require engineered feature extraction | Strong at pattern recognition | Learned perception feeding structured reasoning |
| Compositional reasoning | Native strength (explicit variables, logic) | Often implicit, can fail at systematic generalisation | Neural modules interfaced with symbolic planners / constraint solvers |
| Transparency / Explainability | High (traceable inference chains) | Low / post‑hoc explanations needed | Combine introspectable logic layers with learned embeddings |
| Safety / Guarantees | Amenable to verification | Hard to certify globally | Verified symbolic shells constraining neural proposals |


Together, the comparison table and action items outline a design pattern: apply neural components where raw variability and high-dimensional pattern learning are indispensable; elevate symbolic layers where structure, guarantees, or interpretability dominate requirements; and build deliberate interfaces (aligned representations, constraints, verification hooks) so that signal flows and logical abstractions co-evolve instead of competing. The practical decision is rarely “symbolic versus neural” but how to sequence, couple, and govern them.

### Integration Blueprint (Symbolic ↔ Subsymbolic)

This interim step captures how the limitations (Section 4) map to concrete architectural integration choices. A practical hybrid stack typically (i) grounds perception in neural encoders; (ii) elevates intermediate, semantically meaningful representations (regions, shapes, relations); (iii) applies symbolic/spatial logic to enforce constraints or derive higher‑order features; and (iv) feeds verified outputs into decision or reporting layers. Tooling (e.g. VoxLogicA) acts as the bridge where declarative specifications interrogate or validate learned outputs.

Medical imaging exemplifies hybrid needs: raw voxel data require high‑capacity perceptual extraction, yet clinical utility depends on structured interpretation and safety constraints. Symbolic spatial logics (e.g. VoxLogicA) enable declarative specification of image properties. Neural networks propose segmentations; logical layers can verify, constrain, and provide provenance.

### Synthesis of Author Perspectives
The hybrid AI narrative is a convergence of partially overlapping research agendas. Each of the following perspectives stresses a different bottleneck (scalability, abstraction, safety, causality, modularity) and supplies design levers rather than slogans. Read them as complementary facets of a single engineering objective: dependable generalisation under constraint.

{Add researcher names}

- Symbolic search tradition: Intelligence as symbol manipulation plus heuristic exploration of structured problem spaces.
- Distributed learning tradition: Intelligence emergent from adaptive networks; learning reduces manual knowledge engineering.
- Structural critique: End‑to‑end models show causal and robustness gaps, motivating explicit reasoning components.
- Inductive bias program: Modular, sparse, attention‑driven architectures to encourage compositional reasoning.
- Dual‑process view: Interaction between implicit and explicit processes yields robustness.
- Alignment perspective: Safety and corrigibility require explicit modelling of preferences, goals, and uncertainty.

Taken together these viewpoints converge on a hybrid thesis: future AI must integrate learned perceptual grounding with structured, inspectable reasoning to achieve robustness, generalisation, safety, and alignment in critical domains. The practical payoff is concrete: constraints, modular decomposition, explicit goals, and verifiable properties become first-class architectural components.


# Historical Connections Between Logic and Artificial Intelligence

The relationship between logic and AI is cumulative rather than cyclical. Logic first contributed formal languages and inference rules; later it offered specification and verification techniques; today it reappears inside hybrid pipelines as a means of articulating constraints, auditing behaviour, and structuring knowledge alongside learned representations. The following sections give a scaffolded tour: foundational formalisms, deployment-era expert systems, their evolution into data‑driven medical AI, and the contemporary reintegration under hybrid paradigms.

## Early Roots: Logic and Reasoning
Early logical systems supplied the abstraction machinery (symbols, quantifiers, proof procedures) that made computational reasoning thinkable. They also delineated limits—through incompleteness and undecidability—that still inform feasibility assessments for automated inference. The timeline below highlights inflection points and how each widened the design space for machine reasoning.

| Period | Milestone | Contribution |
|--------|-----------|--------------|
| Antiquity → 19th c. | Aristotelian syllogistics → Frege’s predicate logic | Formal systems for reasoning; basis for symbolic representation. |
| 19th c. | George Boole (Boolean algebra, 1854) | Algebraic formulation of logic, foundation for digital circuits and symbolic computation. |
| 1930s–40s | Gödel, Turing, Church | Limits of logic (incompleteness, decidability) and computational models (Turing machines). |
| 1950s | **Logic Theorist** (Newell & Simon, 1956) | First AI program: proved theorems from *Principia Mathematica*; milestone in automated reasoning. |
| 1960s | Automated theorem proving (Robinson’s resolution, 1965) | Efficient deduction technique; foundation for formal reasoning systems. |
| 1970s | Logic programming (Prolog, Kowalski, 1972) | Unified knowledge representation and inference; widely used in AI and symbolic reasoning. |
| 1980s | Description logics (precursors of OWL) | Structured reasoning for ontologies, medical informatics, semantic web. |
| 1990s–2000s | Knowledge representation, semantic web | Ontology-based reasoning integrated into web standards. |
| 2010s–today | Hybrid AI (neural-symbolic) | Combines statistical learning with logic-based reasoning. |

👉 Logic provided **formalisms, inference methods, and knowledge representation** that shaped entire generations of AI systems.

## Expert Systems: From Prototypes to Real-World Deployment

{Add a textual paragraph to expand the following line; do the same for each subsection}

Expert systems (1970s–1980s) were the first major wave of AI to leave the lab and enter industrial/medical practice.

### Canonical Academic Prototype

| System | Domain | Technology | Impact | Limitation |
|--------|--------|------------|--------|------------|
| **MYCIN** (1970s, Stanford) | Medical diagnosis (bacterial infections, blood diseases) | Rule-based inference (~450 production rules) | Demonstrated expert-level reasoning could be encoded in rules | Not deployed clinically (legal/ethical concerns) |

### Canonical Industrial Success

| System | Domain | Technology | Impact | Use |
|--------|--------|------------|--------|-----|
| **XCON (R1)** (late 1970s–1980s, DEC) | Computer system configuration (VAX computers) | Rule-based expert system (>2500 rules) | Saved DEC significant annual cost | Deployed in production, reduced costly errors |


### Other Deployed Expert Systems

| System | Domain | Technology | Real-World Use |
|--------|--------|------------|----------------|
| **DENDRAL** (1960s–70s, Stanford) | Chemistry (mass spectrometry) | Rule-based, hypothesis generation | Used by chemists; published scientific papers |
| **PROSPECTOR** (1970s–80s) | Mineral exploration | Rule-based inference | Identified a molybdenum deposit that became a working mine |
| **PUFF** (1980s, Stanford) | Pulmonary function diagnosis | Knowledge-based medical inference | Deployed in hospitals for years in lung disease diagnostics |
| **CADET** (1980s, US Air Force) | Military planning & logistics | Planning + reasoning engine | Used operationally for contingency planning |
| **CLIPS** (1980s, NASA) | General-purpose expert system shell | Rule-based, forward chaining | Used in various NASA projects; still maintained today |

### Medical AI Beyond Expert Systems

{here make 5-6 paragraphs or more, detail the evolution of the system, and be accurate on actual, current systems; chose 3-4 major ones and for each detail producer, application field, techniques used if known, pricing range if known. Verify your claims twice using reliable web sources}

In later decades, medical AI evolved beyond symbolic expert systems:

| Era | Approach | Example | Contribution |
|-----|----------|---------|--------------|
| 1980s–90s | Knowledge-based expert systems | MYCIN, PUFF | Reasoning from rules and clinical knowledge |
| 2000s–2010s | Statistical learning, radiomics | Feature extraction from medical images | Linked imaging to prognosis and treatment |
| 2010s–today | Deep learning, hybrid AI | Zebra Medical Vision, IBM Watson for Oncology | Automated image analysis and decision support |

## Radiomics in the Image Processing Pipeline

{What is radiomics? Present it as a general form of "algorithmic" feature extraction.}
Radiomics sits **after image acquisition and pre-processing, but before predictive modeling**:

1. **Image acquisition** (CT, MRI, PET, X-ray).  
2. **Pre-processing** (normalization, noise reduction, segmentation).  
3. **Feature extraction** (radiomics: quantitative features like shape, texture, intensity).  
4. **Data integration** (with clinical/genomic info).  
5. **Modeling & prediction** (ML/AI models for diagnosis, prognosis, therapy planning).  


## Symbolic Artificial Intelligence

Symbolic Artificial Intelligence, also known as **classical AI** or **logic-based AI**, refers to approaches that represent knowledge and reasoning explicitly through symbols and rules. In this paradigm, the world is modeled in terms of entities, their properties, and relationships, making it possible to perform logical inference, planning, and problem solving. This contrasts with subsymbolic methods, such as neural networks, which operate on numerical data without explicit symbolic structures.
