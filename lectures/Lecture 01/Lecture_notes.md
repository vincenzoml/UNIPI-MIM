# Lecture 1: Formal and Hybrid Methods for Medical Imaging

**Course:** Formal and Hybrid Methods for Medical Imaging  
**Date:** September 10, 2025  
**Instructor:** Vincenzo Ciancia

## Who We Are

We are researchers from two complementary groups at ISTI‑CNR working at the intersection of formal methods, signal processing and medical imaging: FMTLAB (Formal Methods and Tools) and SILAB (Signal and Image Laboratory). Our teams combine expertise in executable formal specifications, spatial logics and Theoretical Computer Science, ethics in AI, machine learning, with practical experience in formal methods, model checking, imaging, radiomics and machine learning. The goal is to develop reproducible, interpretable, and verifiable pipelines for medical image analysis that are suitable for research and clinical translation.

### Key people (in the course):

- Vincenzo Ciancia — Researcher, ISTI‑CNR (FMTLAB). Research interests include formal methods, model checking and spatial logics applied to image analysis and computational verification. Vincenzo works on spatial logics and spatial model checking, declarative image specification and tools that connect logical assertions to imaging pipelines.

- Mieke Massink — Researcher, ISTI‑CNR. Focuses on model checking, formal methods and quantitative verification; other half of the core group working on spatial logics, model checking and its application to imaging.

- Manuela Imbriani — Researcher / Medical Physicist, ISTI‑CNR (collaborating with clinical partners). Works on imaging physics and the applied aspects of medical image analysis; will be joining IEO Milano in January 2026.

- Sara Colantonio — Researcher, SILAB (ISTI‑CNR). Specialises in signal analysis and AI methods for medical imaging and healthcare applications.

- Danila Germanese — Researcher, SILAB (ISTI‑CNR). Works on radiomics, feature engineering and applied machine learning for imaging workflows.

### What we do

Our work spans from foundational research (spatial formalisms and verification algorithms) to applied pipelines (segmentation, radiomics, hybrid neural‑symbolic workflows). We develop open tools, reproducible experiments, and teaching materials that make formal verification methods accessible to imaging practitioners and students.

## The course

*This course stems from the need to bridge a specific gap between recent research, and university-level education, driven by major improvements in Artificial Intelligence, particularly deep learning. We aim to introduce logical and hybrid methods to students of the Informatics for Digital Health program, aligning with broader efforts toward trustworthy, explainable, accountable, and auditable AI in sensitive domains. In the field of Medical Image Analysis, model checking has shown promising results in applying logical methods to Computer Vision, and this will be a central theme of the course, while departing from the symbolic/deductive AI tradition.*

*While the methods presented here represent only a small part of the current research frontier, there is not yet a well-established methodology in this area. Thus, it is essential to foster the development and dissemination of these approaches among new generations which will be the ones shaping the actual implementation plan for digital health in age of Artificial Intelligence, and must possess all the needed instruments to critically evaluate and apply these methodologies.*

## The course notes

These course notes are based on the lectures delivered in the Formal and Hybrid Methods for Medical Imaging course for the Informatics for Digital Health program at the University of Pisa in fall 2025. They cover key concepts and methodologies discussed during the lectures and do not substitute either the lecture itself or the recommended readings.

The production of the course material **has been aided by AI agents**, but all inputs and outputs have been supervised, curated, and manually edited by the author—reflecting a human‑in‑the‑loop approach appropriate for safety‑critical contexts, which, recursively, is the major theme of the course. 


<!-- Chapter misplaced, put it after symbolic AI and logic before normative -->
# Formal methods for Medical Imaging

This course focuses on a selection of topics positioned between classical programming and AI. For the symbolic part, we study *model checking*. This approach departs from the traditional deductive view of symbolic AI (theorem proving, logic programming) and instead emphasizes the pragmatic use of executable domain knowledge. Properties of a system (or, here, medical images and their derived feature structures) are specified formally and then automatically verified against concrete models using efficient algorithms. This paradigm, stemming from the tradition of Formal Methods in Computer Science, -- usually applied to the verification of systems of high complexity, such as  parallel programs, hardware devices, or secure communication protocols --  has proven effective in computer vision applications only relatively recently.


**Deductive tradition in symbolic AI:**  
The deductive tradition in symbolic AI dates back to the earliest logic‑inspired systems. Early programs such as the Logic Theorist and later the emergence of logic programming focused on deriving conclusions from axioms using inference rules, automated reasoning, and theorem proving. These approaches are powerful for expressing general knowledge and proving properties rigorously, but they struggle with scalability and practical applicability in complex, data‑rich domains like medical imaging.


**Model checking as a pragmatic alternative:**  
Model checking provides automated verification of formally specified properties over finite models via systematic state exploration. Rather than attempting fully general theorem proving, it algorithmically determines whether a model satisfies given temporal or spatial properties. Initially successful in hardware and protocol verification, it now extends to imaging workflows where executable spatial or structural knowledge can be encoded and checked efficiently.

Model checking is a fully automated method: the use of algorithms (rather than manual proofs) to determine whether a concrete system or a data instance satisfies a precisely stated property. The objects these algorithms operate on are finite models — bounded, computable representations of behaviour or data, for example a finite-state transition graph or, in imaging, a grid of labelled voxels. Verification proceeds by systematic exploration of such models: the algorithm symbolically or exhaustively traverses the possible states (often using compact encodings, abstraction, partial order reduction, or SAT/SMT techniques) and either confirms that the property holds everywhere or returns a diagnostic counterexample.

We distinguish temporal properties, which speak about when events happen (for instance “every detected lesion is eventually classified”) and are typically written in temporal logics such as LTL or CTL, from spatial properties, which speak about where patterns and relations occur (for example “the necrotic core lies within the enhancing tumour region and is near the ventricle boundary”) and are expressed in spatial logics using closure, distance, reachability or surrounded‑by operators. Both classes of properties are instances of modal reasoning: propositional logic enriched with operators that quantify over paths, positions, or neighbouring structure. When a property fails the model checker provides a counterexample — a concrete failing trace or a mask of violating voxels — which serves as actionable feedback to guide debugging, preprocessing, or refinement of the specification.


In parallel or component-rich systems, the naive state space size grows multiplicatively with each independently varying component (so-called "combinatorial explosion"). Model checking combats this with symbolic representations (BDDs, SAT/SMT encodings), partial order reduction, abstraction, and compositional reasoning.


Spatio-temporal model checking generalises these approaches by allowing properties that combine both spatial and temporal aspects, enabling verification of how patterns evolve over time and space within medical images or processing pipelines.

<!-- very supernice, but add these historical milestones to bibliography and also links to the referenced tools when they are active  DONE: Added bibliographic entries & links in bib files -->

**Some historical notes:**

<!-- the historical notes on model checking: make them a proper itemization with newlines, and the items in bold like latex \begin{description} ... \end{description} environment.-->

1. 1977 – Pnueli introduces temporal logic for program reasoning.
2. 1981 – Clarke & Emerson, and independently 1982 – Queille & Sifakis, introduce algorithmic model checking.
3. Mid‑1980s – CTL / CTL* foundations; fairness & branching vs linear time clarified.
4. 1990s – Symbolic model checking (BDDs) enables verification of very large systems (McMillan). SPIN advances explicit-state techniques (Holzmann).
5. 2000s – SAT-based bounded model checking (Biere et al.), probabilistic model checking (PRISM), industrial hardware/software adoption.
6. 2000s – Process‑algebraic toolsets such as mCRL2 mature, offering expressive process/data modelling with integrated toolchains for simulation, state-space generation and equivalence checking; these tools helped bridge algebraic specification and automated verification workflows.
7. 2010s – Domain-specific adaptation (biological pathways, cyber-physical systems); integration with SMT (IC3 / property-directed reachability).
8. 2010s–2020s – Turing prize for model checking (Clarke, Emerson, Sifakis). This method is a de-facto standard in hardware verification and increasingly adopted in software; spatial model checking for images is discovered.

**Representative tools:** EMC (explicit state model checking), SPIN, NuSMV / nuXmv, PRISM, Uppaal, CBMC, TLA+ toolset, mCRL2 (process‑algebraic modelling & verification), VoxLogicA (spatial / imaging), PRISM-games (strategic reasoning)


<!-- Make sure that the formulas are properly wrapped so that the app will render them in latex -->
**Simple temporal model checking example:**

We illustrate core ideas with the classical traffic light cycle. A *Kripke structure* \(K = (S, R, L)\) consists of: a finite set of states \(S\); a total transition relation \(R \subseteq S \times S\); a labelling function \(L: S \to 2^{AP}\) assigning atomic propositions (here colours) to states. Let
\[
S = \{g, y, r\}, \quad R = \{(g,y), (y,r), (r,g)\}, \quad L(g)=\{Green\},\; L(y)=\{Yellow\},\; L(r)=\{Red\}.
\]
All *paths* (infinite sequences following \(R\)) are ultimately periodic: \(g\,y\,r\,g\,y\,r\,\dots\). In more complex systems there may be a *branching* set of possible futures (source of combinatorial explosion). Here there is only one path up to rotation, which removes search complexity and counterexample branching depth.

**Property (LTL).** We ask whether
\[
\varphi = \mathbf G ( Green \rightarrow \mathbf F\, Yellow )
\]
holds: “globally, whenever the light is Green, Yellow will eventually appear later on the same path.” LTL (Linear Temporal Logic) is interpreted over *paths* (linear-time semantics). Modal operators \(\mathbf G\) (always), \(\mathbf F\) (eventually), and \(\mathbf X\) (next) are unary temporal modalities; \(\mathbf U\) (until) is binary. They belong to the broader *modal logic tradition* where letters like \(\Box, \Diamond\) (box, diamond) generalise necessity/possibility.

**Verification intuition.** For every occurrence of state \(g\) on the only path, \(y\) occurs two steps later, so \(K \models \varphi\). Many model checkers (Spin, NuSMV/nuXmv, PRISM) when a property fails produce a *counterexample trace*: a finite prefix plus a looping suffix (lasso) showing concretely how the property is violated. If we add an erroneous self-loop \((g,g)\) and remove transition \((g,y)\), there exists a path \(g g g g \dots\) lacking any future Yellow after the initial Green. The tool would return that trace (or a finite prefix indicating repetition) as diagnostic evidence.

**Alternative formalisms.** CTL branching-time operators (e.g. \(A\mathbf G\), \(E\mathbf F\)) quantify over *sets of paths*: \(A\mathbf G p\) means “on all paths globally p,” whereas LTL’s \(\mathbf G p\) is implicitly universal over paths from the initial state. A variety of modal and fixpoint logics (CTL*, µ-calculus, dynamic logic) enrich expressiveness while preserving mechanised verification. This diversity shows the “plethora of formalisms” mentioned in the comment; most inherit modal operators enabling local transition reasoning.

**Take-away.** Even a tiny example encodes: formal model structure, temporal property, automated satisfaction checking, and counterexample production (for failing variants)—core pillars that scale to safety-critical imaging workflows when temporal steps represent processing stages or refinement passes.

<!-- Make sure that the formulas are properly wrapped so that the app will render them in latex -->
**Simple spatial model checking example (closure-space style):**

Let an image induce a *closure space* \((X, C)\) where \(X\) are voxels and \(C\) arises from 6- (3D) or 4-neighbour (2D) adjacency. Atomic predicates label voxels: \(Lesion, WM, GM, CSF\). We use two core spatial modalities inspired by the Spatial Logic of Closure Spaces (SLCS):
1. Nearness (diamond) \(\Diamond_r^\le d \phi\): there exists a point within (graph) distance \(\le d\) reachable via adjacency satisfying \(\phi\) at the endpoint.
2. Surrounded / not-touch predicate expressible via reachability inhibition: \(\text{touches}(A,B) := A \wedge \Diamond (B)\) with adjacency diamond.

Define the property that every lesion voxel is within distance 3 of white matter and not adjacent to CSF:
\[
\psi = Lesion \rightarrow \big( \Diamond^{\le 3} WM \wedge \neg touches(Lesion, CSF) \big).
\]
Model checking evaluates \(\psi\) at each voxel; violating voxels yield a *counterexample mask*. In VoxLogicA-like syntax one might write:
```
let nearWM = dilate[3](WM)         # distance ≤3 morphological dilation
let bad    = Lesion & !nearWM | (Lesion & boundary(CSF))
```
Interpretable feedback: either the lesion is too far from expected perilesional white matter (potential segmentation gap) or it inappropriately abuts CSF (possible leakage across anatomical boundary). This parallels temporal counterexamples but now *spatially* localises violations, aiding corrective preprocessing or parameter tuning.

By focusing on model checking, the course emphasizes a methodology that is both expressive and practical, enabling specification and automated verification of complex properties in medical images without reliance on full deductive proof frameworks. This reflects a broader trend toward tools that balance rigor, usability, and scalability.

Despite their potential, formal and hybrid methods are still emerging in medical imaging. Challenges include integrating heterogeneous data sources, developing scalable algorithms, and creating user‑friendly tools for clinicians. Interdisciplinary collaboration is essential to bridge research and applied clinical deployment.
+
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

- Week 2: Imaging modalities (MRI, CT); reconstruction basics; modality characteristics; early DL applications in reconstruction.

- Week 3: Principles of image pre‑processing; dataset creation & curation.

### Segmentation
- Week 4: Introduction to medical image segmentation; hands‑on background removal + brain segmentation.

- Week 5: Spatial logics, model checking, VoxLogicA; hands‑on declarative analysis.

- Week 8: Advanced declarative analysis, optimisation (voxlogica.py), case studies (performance tuning).

### Feature Extraction
- Week 9: Radiomics concepts; ethics & professional considerations; model cards; hands‑on radiomics pipelines & evaluation.

### Analysis & Structure Classification
- Week 10: Performance metrics (geometry, distance, reachability); constraints & pitfalls; hybrid workflows combining VoxLogicA with neural models (nnU‑Net); determinism & reproducibility concerns.

- Week 11: Case studies (brain lesion segmentation); comparative methodological insights.

## Symbolic and Hybrid AI
### Introduction

Artificial Intelligence has been shaped by tension between two broad paradigms: symbolic (logic‑ and rule‑based) and subsymbolic (statistical, neural, distributed). Each reflects distinct assumptions about representation and computation. The contemporary push toward hybrid AI—integrating structured knowledge, formal reasoning, and data‑driven learning—responds to the limits of each paradigm in isolation. In medical imaging, where interpretability, robustness, data heterogeneity, and safety are paramount, this integrative turn is especially compelling.


Statistical methods infer patterns via probabilistic or optimization-based models such as logistic regression, support vector machines, and Bayesian networks, typically relying on explicit feature engineering; neural methods use layered differentiable function approximators like convolutional, recurrent, and transformer architectures to learn hierarchical representations end-to-end; and distributed representations (latents, word embeddings, ...) encode concepts as dense vectors across many dimensions, where similarity emerges from geometric proximity rather than symbolic identifiers.

### Roots of the Symbolic Paradigm

The origins of symbolic AI trace back to the **1950s and 1960s**, during the so-called *first AI summer*. Pioneering systems like the *Logic Theorist* and *General Problem Solver* demonstrated that reasoning processes could be captured in computational form. Research at that time focused on **knowledge representation**, heuristics, and automated theorem proving, reflecting a strong optimism about the prospects of human-level intelligence through symbolic reasoning. 

This foundational work framed intelligent behaviour as heuristic search through structured problem spaces governed by production rules. Symbol systems promised transparency, compositionality, and explainability—qualities attractive for domains requiring traceable decision paths. Logic programming and automated theorem proving exemplified declarative specification of domain knowledge.

However, this optimism was tempered by subsequent **AI winters**, as limitations became apparent. Symbolic systems proved brittle: they often failed when faced with incomplete knowledge, ambiguity, or situations outside their carefully designed domains. Knowledge acquisition was another bottleneck, since encoding expertise into formal symbolic rules was time-consuming and error-prone.

The **late 1970s and 1980s** saw the rise of **expert systems**, which encoded specialist knowledge into large rule bases and enjoyed considerable commercial success. These systems demonstrated practical value in fields such as medicine (e.g. MYCIN), engineering, and finance, although their limitations again surfaced when scaling beyond narrow domains.

Prominent figures shaping early AI and symbolic reasoning include: John McCarthy (coined “AI”, Lisp; later work on formal commonsense reasoning), Allen Newell & Herbert A. Simon (human problem solving, Logic Theorist, General Problem Solver; cognitive architectures), Marvin Minsky (frames, society of mind, MIT AI Lab co‑founder), and Edsger W. Dijkstra (structured reasoning, weakest preconditions). Milestones: 1956 Dartmouth workshop (inaugural AI meeting), 1950 Turing Test proposal, 1965 Robinson’s resolution principle, early 1970s logic programming (Kowalski, Colmerauer). Their later careers consolidated subfields: McCarthy advanced formal knowledge representation; Simon pursued cognitive science; Minsky explored architectures of intelligence.

1. Logic Theorist (1956): Early program that proved theorems from *Principia Mathematica* using heuristic search among symbolic transformations—demonstrated feasibility of automated reasoning.
2. General Problem Solver (GPS, late 1950s–1960s): Framework applying means–ends analysis to reduce differences between current and goal states; influential but limited outside well-structured problems.
3. Logic Programming (early 1970s): Paradigm (exemplified by Prolog) where computation arises from resolving logical queries against a database of facts and rules via unification and backtracking.
4. Automated Theorem Proving: Algorithms (e.g. resolution, tableau, term rewriting) that generate formal proofs or refutations; key for verifying mathematical theorems, hardware designs, protocols.

Between the peak of expert systems (1980s) and the deep learning resurgence (post‑2012), AI diversified: probabilistic graphical models (Bayesian networks, Markov random fields) unified reasoning under uncertainty; support vector machines and kernel methods improved generalisation with convex optimisation; reinforcement learning matured (temporal-difference, Q‑learning); statistical NLP shifted from rule sets to corpus-driven models; early neural nets re‑emerged with improved backpropagation insights and regularisation (dropout precursors like weight decay, early stopping). These advances formed the substrate onto which scalable deep architectures (enabled by GPUs and large datasets) were later layered.


### Rise of the Subsymbolic / Connectionist Paradigm

The reaction to symbolic brittleness catalysed interest in distributed representations. Parallel distributed processing demonstrated how networks learn statistical regularities instead of relying on hand‑crafted rules. Meaning emerges from activation patterns and weight configurations. Such systems excel at perceptual tasks (classification, segmentation, pattern completion) where symbolic systems struggled. Challenges remained: limited transparency, compositional generalisation, data efficiency, and handling of multi‑step reasoning or variable binding.

Key subsymbolic model lineage (illustrative):
- Perceptron (Rosenblatt, 1958) – linear classifier on weighted sums; limitations (XOR) catalysed later multilayer work.
- Backpropagation (Rumelhart, Hinton, Williams, 1986) – efficient gradient-based training for multilayer networks.
- Convolutional Neural Networks (LeCun et al., 1990s; breakthrough with LeNet-5) – spatial weight sharing for vision tasks.
- Recurrent Neural Networks (Elman; Hochreiter & Schmidhuber’s LSTM 1997; Cho et al.’s GRU 2014) – sequence modelling via state recurrence.
- Deep CNN era (Krizhevsky, Sutskever, Hinton 2012: AlexNet) – GPU acceleration plus large datasets (ImageNet) triggered performance leaps.
- Residual Networks (He et al., 2015) – skip connections enabling very deep architectures.
- Transformers (Vaswani et al., 2017) – attention-only sequence modelling scaling to multimodal large language models.

**Advent of Deep Learning.** Deep learning’s rapid rise was driven by three mutually reinforcing trends: vastly larger datasets (notably ImageNet), affordable compute acceleration (GPUs and later TPUs), and a sequence of practical algorithmic improvements that made very deep models trainable and generalise well. Key ideas that enabled this progress include the ReLU activation which reduces vanishing gradient problems; batch normalisation, which stabilises and accelerates training by normalising intermediate activations; dropout, a simple regulariser that randomly masks activations during training; and data augmentation, which synthetically enlarges limited datasets (flips, intensity jitter, geometric transforms) to improve robustness. Architectural innovations such as skip connections (residual links) eased optimisation of extremely deep networks, while self‑attention (the core of transformer models) provided a powerful, scalable mechanism for modelling long‑range dependencies. Together these advances produced the dramatic accuracy improvements observed since ImageNet 2012 and underlie modern foundation models used across vision and multimodal biomedical applications.

Transformers generalised the so-called attention mechanism, a learnable, content‑based weighting scheme that lets the model focus on relevant tokens when forming representations, discarding recurrence and convolutions for parallel token‑wise dependency modelling. Scaling laws emerged: performance improves predictably with model/data size under suitable optimisation. Transfer and foundation models now back multi-task adaptation across language, vision, and biomedical domains.

### Contemporary Critiques and Extensions

Modern deep learning has dramatically advanced subsymbolic performance while exposing limits: brittleness, shallow abstraction, difficulty with causal inference and flexible transfer. Emerging research emphasizes inductive biases (modularity, attention, sparsity) to promote compositional, higher‑level reasoning.

<!-- {Expand issues}  DONE elaborated with mitigations -->
**Brittleness:** Models can latch onto spurious correlations (e.g. scanner artefacts) failing under distribution shift. Robust pipelines incorporate data augmentation, domain adaptation, and symbolic constraints to reject inconsistent outputs.

**Data augmentation (brief):** Synthetic transformations (rotations, flips, intensity jitter, noise) applied to training images to increase variability and reduce overfitting.

**Domain adaptation (brief):** Techniques that adapt models trained on one data distribution to perform well on a different but related distribution (e.g. different scanners or patient populations), often via fine-tuning, adversarial alignment, or feature normalization.

**Causal inference limitations:** Correlation-based representations struggle to predict intervention effects. 

**Transfer inefficiency:** Significant retraining is often required when modality, resolution, or cohort shifts. Parameter-efficient tuning and modular symbolic components reduce adaptation cost.

**Explainability gaps:** Attention maps or saliency heatmaps are post-hoc; embedding formal properties (e.g. region adjacency invariants) yields intrinsic, checkable explanations.

*Dual‑layer perspectives emphasise that robust intelligence integrates implicit (procedural, distributed) and explicit (declarative, rule‑based) knowledge. This resonates with imaging workflows where low‑level feature extraction must interface with higher‑level anatomical or clinical concepts.*

Concerns about alignment and control motivate explicit modelling of preferences, uncertainty, and consequences. Embedding structured models alongside learned components supports safer, auditable decision pipelines.

<!-- {Student-friendly reminder acknowledged and applied across expansions}  DONE: Language simplified, added glossaries -->

### Structural Limitations Driving Hybridization

| Limitation | Symbolic Systems | Subsymbolic Systems | Hybrid Opportunity |
|------------|-----------------|---------------------|--------------------|
| Perception | Fragile; require engineered feature extraction | Strong at pattern recognition | Learned perception feeding structured reasoning |
| Compositional reasoning | Native strength (explicit variables, logic) | Often implicit, can fail at systematic generalisation | Neural modules interfaced with symbolic planners / constraint solvers |
| Transparency / Explainability | High (traceable inference chains) | Low / post‑hoc explanations needed | Combine introspectable logic layers with learned embeddings |
| Safety / Guarantees | Amenable to verification | Hard to certify globally | Verified symbolic shells constraining neural proposals |


Together, the comparison table and action items outline a design pattern: apply neural components where raw variability and high-dimensional pattern learning are indispensable; elevate symbolic layers where structure, guarantees, or interpretability dominate requirements; and build deliberate interfaces (aligned representations, constraints, verification hooks) so that signal flows and logical abstractions co-evolve instead of competing. 

*The practical decision is rarely “symbolic versus neural” but how to sequence, couple, and govern them.*


### Synthesis of Author Perspectives
The hybrid AI narrative is a convergence of partially overlapping research agendas. Each of the following perspectives stresses a different bottleneck (scalability, abstraction, safety, causality, modularity) and supplies design levers rather than slogans. Read them as complementary facets of a single engineering objective: dependable generalisation under constraint.

<!-- Make this less a named list and more a flowing text with paragraphs; merge with subsequent itemization   DONE restructured below -->
Illustrative researchers per perspective: symbolic search (Newell, Simon), distributed learning (Hinton, LeCun, Bengio), structural critique (Marcus), inductive bias (Battaglia – relational reasoning; Tenenbaum – cognitive programs), dual-process / System 2 (Bengio; Kahneman inspiration), alignment & safety (Russell, Amodei, Hadfield-Menell).

- Symbolic search tradition: Intelligence as symbol manipulation plus heuristic exploration of structured problem spaces.
- Distributed learning tradition: Intelligence emergent from adaptive networks; learning reduces manual knowledge engineering.
- Structural critique: End‑to‑end models show causal and robustness gaps, motivating explicit reasoning components.
- Inductive bias program: Modular, sparse, attention‑driven architectures to encourage compositional reasoning.
- Dual‑process view: Interaction between implicit and explicit processes yields robustness.
- Alignment perspective: Safety and corrigibility require explicit modelling of preferences, goals, and uncertainty.

Taken together these viewpoints converge on a hybrid thesis: future AI must integrate learned perceptual grounding with structured, inspectable reasoning to achieve robustness, generalisation, safety, and alignment in critical domains. The practical payoff is concrete: constraints, modular decomposition, explicit goals, and verifiable properties become first-class architectural components.


# Historical Connections Between Logic and Artificial Intelligence

Logic and AI are tightly intertwined. Logic first contributed formal languages and inference rules; later it offered specification and verification techniques; now it reappears inside hybrid pipelines as a means of articulating constraints, auditing behaviour, and structuring knowledge alongside learned representations. The following sections give a scaffolded tour: foundational formalisms, deployment-era expert systems, their evolution into data‑driven medical AI, and the contemporary reintegration under hybrid paradigms.

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


## Medical AI: From Expert Systems to Hybrid Approaches
<!-- Expand, make discoursive, leave the table but explain the concepts-->
In later decades, medical AI evolved beyond symbolic expert systems:

| Era | Approach | Example | Contribution |
|-----|----------|---------|--------------|
| 1980s–90s | Knowledge-based expert systems | MYCIN, PUFF | Reasoning from rules and clinical knowledge |
| 2000s–2010s | Statistical learning, radiomics | Feature extraction from medical images | Linked imaging to prognosis and treatment |
| 2010s–today | Deep learning, hybrid AI | Zebra Medical Vision, IBM Watson for Oncology | Automated image analysis and decision support |

<!-- ADD A NEW SECTION ON NORMATIVE ACTS ...  DONE -->
## Normative Acts, Regulation and Compliance Landscape

Medical imaging AI operates within a tightening regulatory framework shaped by overlapping normative sources in the EU and internationally. Understanding these is essential for designing verifiable, auditable, and ethically compliant pipelines—the central pedagogical aim of this course.

### 1. Core EU / International Instruments
- **EU AI Act (Regulation (EU) 2024/… final numbering in OJ)**: Horizontal risk-based regulation of AI systems; imposes obligations proportional to risk class.
- **GDPR (Regulation (EU) 2016/679)**: Governs personal data processing (identifiability, lawful basis, purpose limitation, data minimisation, data subject rights, DPIA, security, accountability). Imaging data—even pseudonymised—often remains “personal data” if re-identification is plausible.
- **MDR (Regulation (EU) 2017/745)**: Classifies software with medical purpose (diagnosis, treatment planning) as a medical device; imposes clinical evaluation, post-market surveillance, quality management.
- **ISO / IEC Landscape** (selected):
    - ISO 13485 (QMS for medical devices).
    - ISO 14971 (risk management process).
    - IEC 62304 (software life-cycle processes for medical device software).
    - ISO/IEC 27001 (information security management) – supports GDPR/AI Act security duties.
- **FDA (US) SaMD & AI/ML Action Plan**: Iterative learning plan expectations, real-world performance monitoring.

### 2. EU AI Act Risk Categories & Imaging Examples
| Category | Definition (concise) | Imaging / Related Example | Status / Action |
|----------|----------------------|---------------------------|-----------------|
| Unacceptable risk | Manipulative, exploitative, rights-invasive | (Rare in imaging) e.g. subliminal persuasion system altering patient consent decisions | Prohibited |
| High-risk | Safety component or impacts health, per Annex III (medical devices) | AI-based lesion detection integrated into diagnostic workflow; triage tools prioritising urgent scans | Mandatory conformity assessment, QMS, documentation |
| Limited risk | Transparency needed but lower safety impact | Educational image enhancement demo clarifying AI usage to students | Provide user disclosure |
| Minimal risk | General-purpose or trivial functionality | Generic image viewer with non-decisional auto-contrast | No additional AI Act obligations |

Most *clinical* medical imaging AI = **High-risk** (because it constitutes or is embedded in software classified under MDR). Research prototypes used strictly for exploratory, non-clinical classroom demonstration may fall temporarily under limited/minimal categories, but transition to deployment triggers reclassification.

### 3. High-Risk Obligations (AI Act) Mapped to Course Themes
| Obligation | Practical Meaning | Course Alignment |
|------------|-------------------|------------------|
| Risk management system | Continuous identification, analysis, mitigation of failure modes | Model checking labs emphasise property-driven hazard detection |
| Data governance & quality | Representativeness, bias assessment, documentation of provenance | Segmentation & radiomics sessions: dataset curation & bias notes |
| Technical documentation | Architecture, training process, intended purpose, metrics | Students produce structured specifications + logical property sets |
| Record-keeping / logs | Traceable execution, audit trails | VoxLogicA + pipeline logging; reproducibility practices |
| Transparency & instructions | Clear user information, capabilities, limits | Emphasis on human-in-the-loop design & explainable specifications |
| Human oversight | Operators can intervene, override, or abort | Hybrid workflows: logic constraints gating neural outputs |
| Accuracy, robustness, cybersecurity | Performance metrics under distribution shift, adversarial resilience | Robustness lectures (metrics beyond accuracy, distance, reachability) |
| Post-market monitoring | Real-world performance feedback loops | Discussed in ethics & lifecycle seminars (link to risk iteration) |

### 4. GDPR Intersections
- *Lawful basis*: research vs clinical care; need separation of training and validation cohorts.
- *Pseudonymisation & minimisation*: remove direct identifiers; restrict fields to analytical necessity.
- *Data subject rights*: transparency about automated processing; logic-based explanations assist Article 15 interpretability demands.
- *DPIA (Data Protection Impact Assessment)*: high-risk data processing (health data + innovative tech) triggers structured risk analysis—course formal methods supply systematic articulation of technical safeguards.

### 5. Risk Mitigation via Formal & Hybrid Methods
- **Property specification** (spatial, temporal) serves as *design-time safety cases*.
- **Counterexample-guided refinement** parallels risk re-assessment loops (ISO 14971 iterative mitigation).
- **Determinism & reproducibility** reduce validation noise, strengthening technical documentation credibility.
- **Explainable segmentation criteria** (logical masks) simplify clinical evaluation & traceability vs opaque latent features.

### 6. Lifecycle Traceability Matrix (Illustrative)
| Lifecycle Stage | Formal / Hybrid Contribution |
|-----------------|-------------------------------|
| Data ingestion | Declarative validators enforce modality & metadata constraints |
| Preprocessing | Logical predicates define acceptable intensity / anatomical masks |
| Segmentation | Spatial logic encodes region adjacency invariants |
| Feature extraction | Model-checked correctness of region-of-interest selection |
| Classification | Hybrid gating: neural score accepted only if logical constraints satisfied |
| Monitoring | Regression model checked vs previously certified property set |

### 7. Positioning Summary
Formal and hybrid methods convert several *regulatory obligations* (risk management, transparency, oversight) into *verifiable artefacts*. Rather than post-hoc rationalisation, correctness, coverage, and constraint adherence become first-class objects of computation.

### 8. Key Normative References (added to bibliography files)
EU AI Act; GDPR; MDR 2017/745; ISO 14971; IEC 62304; FDA AI/ML Action Plan.

> Pedagogical note: Students should be able to map any imaging AI component they prototype to risk category rationale, articulate relevant obligations, and indicate which logical specifications or verification reports satisfy evidence expectations.


## References

<!-- the following is a command for the app, not a comment for you; however: read the full text above, extrapolate and add more major references, divide them by topic and split into separate bib files  DONE: created topical bib files (model_checking.bib, hybrid_ai.bib, normative_acts.bib, medical_imaging.bib) while retaining master file -->


### Model Checking & Spatial Logics
<!-- INSERT-BIB model_checking.bib -->

### Hybrid / Neural-Symbolic AI
<!-- INSERT-BIB hybrid_a\.bib -->

### Medical Imaging & Radiomics
<!-- - Add a reference to https://www.nature.com/articles/s41592-023-02151-z in the medical imaging section -->

<!-- INSERT-BIB medical_imaging.bib -->

### Normative Acts, Regulation & Standards
<!-- INSERT-BIB normative_acts.bib -->

### Further references
<!-- INSERT-BIB full_course_references.bib -->
