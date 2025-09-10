# Lecture 1: Formal and Hybrid Methods for Medical Imaging

**Course:** Formal and Hybrid Methods for Medical Imaging  
**Date:** September 10, 2025  
**Instructor:** Vincenzo Ciancia

---

---

## The course notes

These course notes have been authored by Vincenzo Ciancia, based on the lectures delivered in the Formal and Hybrid Methods for Medical Imaging course for the Informatics for Digital Health program at the University of Pisa in fall 2025. They cover the key concepts and methodologies discussed during the lecture and do not substitute neither the lecture itself nor the recommended readings.

The production of the course material **has been aided by AI agents**, but both the provided input (including a knowledge base) and the outputs have been supervised, curated, and manually edited by the author. Indeed, this is in the very same spirit of the course: combining human expertise with AI-based tools.  

## The course

This course stems from the need to introduce symbolic and hybrid methods to students and future professionals in the Informatics for Digital Health program. While the methods presented here represent only a small part of the current research frontier, there is not yet a well-established methodology in this area. Thus, it is essential to foster the development and dissemination of these approaches among new generations which will be the ones shaping the actual implementation plan for digital health in the coming decades.

**Focus of the course:**  
This course focuses on a relatively narrow, but quite successful methodology for symbolic AI: *model checking*. Unlike the traditional "deductive" approaches in symbolic AI—such as automated theorem proving and logic programming—model checking emphasizes the pragmatic use of executable domain knowledge. In model checking, properties of a system (or, in our context, medical images and their features) are specified formally and then automatically verified against concrete models using efficient algorithms.

**Deductive tradition in symbolic AI:**  
The deductive tradition in symbolic AI dates back to the origins of artificial intelligence and formal logic in the mid-20th century. Early systems, such as the Logic Theorist (Newell & Simon, 1956) and later Prolog (Colmerauer & Roussel, 1972), focused on deriving conclusions from axioms using inference rules—essentially, automated reasoning and theorem proving. These approaches are powerful for expressing general knowledge and proving properties in a mathematically rigorous way, but they often struggle with scalability and practical applicability in complex, data-rich domains like medical imaging.

**Model checking as a pragmatic alternative:**  
Model checking, introduced in the early 1980s (Clarke & Emerson, 1981; Queille & Sifakis, 1982), departs from pure deduction by providing automated, algorithmic verification of properties over finite models. Instead of attempting to prove theorems in general, model checking tools exhaustively explore all possible states of a system to check whether specified properties hold. This approach has proven highly effective in hardware and software verification, and more recently, in domains such as medical imaging, where executable domain knowledge can be encoded and checked efficiently.

By focusing on model checking, this course emphasizes a methodology that is both expressive and practical, enabling the specification and verification of complex properties in medical images without the need for full-blown deductive reasoning. This shift reflects a broader trend in AI and formal methods towards tools and techniques that balance rigor with usability and scalability.

Despite their potential, symbolic and hybrid methods are still emerging in medical imaging. There are significant challenges to address, including the integration of heterogeneous data sources, the development of scalable algorithms, and the creation of user-friendly tools for clinicians. Moreover, interdisciplinary collaboration is needed to bridge the gap between theoretical research and practical applications in hospitals and clinics.

By fostering knowledge and skills in these areas, the course supports the broader goal of improving patient outcomes, advancing medical research, and ensuring that future professionals are prepared to navigate the challenges and opportunities of an increasingly digital healthcare landscape.

---

## Multidisciplinary, seminar-style structure of the course

This course is intentionally multidisciplinary and delivered in a seminar-style format: multiple experts active at the research frontier contribute lectures, discussions, and hands-on sessions. Rather than a single-perspective treatment, you will encounter complementary viewpoints spanning methodology, clinical/technical imaging practice, and hybrid AI engineering. The rotating instructors (including Vincenzo, Sara, Manuela, Mieke, and Danila) each focus on their domain strengths—ensuring that formal reasoning, imaging physics, data engineering, spatial logics, radiomics, and hybrid AI practices are all grounded in current research questions and real-world constraints.

### Complementary thematic threads (as reflected in the schedule)

- Foundations of paradigms: symbolic, formal, subsymbolic, and hybrid approaches; positioning model checking among verification techniques
- Ethics and human‑centric AI: responsible use, transparency, professional considerations
- Medical imaging physics & modalities: CT / MRI acquisition principles and reconstruction pipelines
- Image reconstruction & enhancement: algorithms, low‑dose strategies, artifact reduction, links to deep learning
- Data engineering & preparation: pipeline design, dataset creation, curation, governance
- Pre-processing & segmentation fundamentals: from theoretical principles to practical brain imaging segmentation
- Spatial logics & declarative image analysis: model checking, VoxLogicA, expressive spatial property specification
- Advanced declarative workflows: performance optimisation, tooling (e.g. voxlogica.py), case study–driven refinement
- Radiomics & machine learning: feature extraction, pipelines, evaluation protocols, model cards, ethical implications
- Performance and constraints: metrics beyond accuracy (geometry, distance, reachability), pitfalls and failure modes
- Hybrid AI integration: combining spatial logic specifications with neural architectures (e.g. nnU-Net), determinism and reproducibility concerns
- Case studies: brain lesion segmentation, brain tissue identification, comparative methodological insights
- Reproducibility & documentation: dataset selection, metrics reporting, traceability, exam preparation

These threads are interleaved: conceptual lectures introduce formal or methodological tools, followed by practical hands-on sessions that expose implementation subtleties, optimisation trade-offs, and ethical or professional implications. You are encouraged to treat the material not as a linear textbook narrative but as a mosaic of interoperable techniques that can be recombined when designing robust, explainable, and clinically relevant imaging workflows.

---

## References and Further Reading

1. **Belmonte, G., Bussi, L., Ciancia, V., Latella, D., Massink, M.** (2024). "Towards Hybrid-AI in Imaging Using VoxLogicA." *ISoLA 2024: Leveraging Applications of Formal Methods*, pp. 205-221. DOI: 10.1007/978-3-031-75387-9_13

2. **Ciancia, V., et al.** (2024). "[Recent Medical Imaging Paper Title]." *[Medical Imaging Journal]*, [Volume], [Pages]. DOI: [DOI] 
   *Note: Please update with specific details of your recent medical imaging publication*

3. **Ciancia, V., Latella, D., Loreti, M., Massink, M.** (2014). "Specifying and verifying properties of space." *Theoretical Computer Science*, 550, 25-41.

4. **Medical Imaging Ethics Guidelines:** IEEE Standards for Medical Device Software, FDA Guidelines for AI/ML-Based Medical Devices

5. **VoxLogicA Tool and Documentation:** Available at the official VoxLogicA repository and ISTI-CNR research pages

6. **Recent Advances in Hybrid AI:** Survey papers on neuro-symbolic AI and explainable AI in healthcare applications

7. Clarke, E.M., Emerson, E.A. (1981). "Design and Synthesis of Synchronization Skeletons Using Branching-Time Temporal Logic." *Logic of Programs*, LNCS 131, pp. 52–71.

8. Queille, J.P., Sifakis, J. (1982). "Specification and Verification of Concurrent Systems in CESAR." *Proceedings of the 5th International Symposium on Programming*, pp. 337–351.

9. Newell, A., Simon, H.A. (1956). "The Logic Theory Machine: A Complex Information Processing System." *IRE Transactions on Information Theory*, 2(3), pp. 61–79.

10. Colmerauer, A., Roussel, P. (1972). "The Birth of Prolog." *Proceedings of the 2nd International Conference on Logic Programming*, pp. 37–52.