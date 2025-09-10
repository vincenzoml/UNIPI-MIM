# Lecture 1: Introduction to Hybrid AI and Formal Methods in Medical Imaging

**Course:** Formal and Hybrid Methods for Medical Imaging  
**Date:** September 10, 2025  
**Instructor:** Vincenzo Ciancia

## Learning Objectives

By the end of this lecture, students will be able to:
- Understand the concept of hybrid AI and its relevance to medical imaging
- Distinguish between symbolic, subsymbolic, and hybrid approaches
- Recognize the role of formal methods in medical image analysis
- Understand the basic principles of VoxLogica and spatial model checking
- Appreciate the ethical considerations in AI-driven medical imaging

---

## 1. Introduction: The Landscape of AI in Medical Imaging (30 minutes)

### 1.1 Traditional Approaches vs. Modern AI

Medical imaging has evolved from purely manual interpretation to sophisticated automated analysis. Today's landscape includes:

**Traditional Image Processing:**
- Rule-based algorithms
- Mathematical morphology
- Feature extraction based on domain knowledge
- Deterministic, interpretable results

**Modern Machine Learning:**
- Deep neural networks (CNNs, U-Net, nnU-Net)
- Data-driven feature learning
- High performance on specific tasks
- Often "black box" with limited interpretability

**The Gap:**
- Traditional methods: interpretable but limited in complex scenarios
- ML methods: powerful but lack transparency and domain knowledge integration

### 1.2 What is Hybrid AI?

Hybrid AI combines the strengths of different AI paradigms:

```
Hybrid AI = Symbolic AI + Subsymbolic AI + Human Knowledge
```

**Key Characteristics:**
- **Complementarity:** Different methods handle different aspects of the problem
- **Interpretability:** Formal methods provide explainable reasoning
- **Robustness:** Multiple approaches reduce single-point failures
- **Domain Integration:** Incorporates medical expertise and constraints

---

## 2. The Three Pillars of AI in Medical Imaging (45 minutes)

### 2.1 Symbolic AI (Formal Methods)

**Definition:** AI based on explicit representation of knowledge using symbols and logical rules.

**In Medical Imaging:**
- Spatial logic for describing anatomical relationships
- Rule-based segmentation using geometric constraints
- Formal verification of image analysis pipelines

**Example:** "A brain lesion is a connected region with intensity > threshold AND distance from ventricles < 5mm"

### 2.2 Subsymbolic AI (Machine Learning)

**Definition:** AI that learns patterns from data without explicit symbolic representation.

**In Medical Imaging:**
- Convolutional Neural Networks for segmentation
- Deep learning for classification
- Generative models for image synthesis

**Example:** A CNN trained on 10,000 brain scans learns to segment tumors without explicit rules.

### 2.3 Hybrid Approaches

**Definition:** Integration of symbolic and subsymbolic methods to leverage both data-driven learning and domain knowledge.

**Strategies:**
1. **Sequential:** ML preprocessing → Formal verification
2. **Parallel:** Multiple methods vote on results
3. **Integrated:** Formal constraints guide ML training
4. **Hierarchical:** Different methods at different scales

---

## 3. Introduction to Formal Methods and Model Checking (30 minutes)

### 3.1 What are Formal Methods?

**Definition:** Mathematical techniques for specification, development, and verification of software and hardware systems.

**Key Components:**
- **Formal specification:** Mathematical description of system behavior
- **Formal verification:** Mathematical proof of correctness
- **Model checking:** Automated verification of finite-state systems

### 3.2 Model Checking in Medical Imaging

**Traditional Model Checking:**
- Verifies software/hardware systems
- Checks if system satisfies temporal logic properties
- Example: "The system never enters an unsafe state"

**Spatial Model Checking:**
- Verifies spatial properties of images
- Checks if image regions satisfy spatial logic formulas
- Example: "All tumor regions are connected and have high intensity"

### 3.3 Why Formal Methods in Medical Imaging?

**Advantages:**
- **Precision:** Exact mathematical specification of requirements
- **Verification:** Proof that analysis meets specifications
- **Interpretability:** Clear reasoning about results
- **Reliability:** Reduced errors in critical medical applications

**Challenges:**
- **Complexity:** Requires mathematical expertise
- **Scalability:** May be computationally intensive
- **Flexibility:** Less adaptable than learning-based methods

---

## 4. VoxLogica: Spatial Model Checking for Medical Images (45 minutes)

### 4.1 What is VoxLogica?

**VoxLogica** is a spatial model checker specifically designed for medical image analysis.

**Key Features:**
- **Spatial Logic:** Describes spatial relationships in images
- **3D Support:** Handles volumetric medical data (MRI, CT)
- **Declarative:** Specify what to find, not how to find it
- **Verification:** Proves properties about image regions

### 4.2 Spatial Logic Fundamentals

**Basic Concepts:**
- **Atomic Propositions:** Basic properties (e.g., "high intensity")
- **Spatial Operators:** Describe spatial relationships
- **Logical Connectives:** AND, OR, NOT, IMPLIES

**Spatial Operators:**
- `near(φ, d)`: Points within distance d of regions satisfying φ
- `surrounded(φ, ψ)`: Regions φ completely enclosed by regions ψ
- `connected(φ)`: Connected components satisfying φ

**Example Formula:**
```
tumor := intensity > 150 AND connected(true)
edema := near(tumor, 10) AND intensity > 100
```

### 4.3 VoxLogica in Practice

**Workflow:**
1. **Image Loading:** Import medical images (DICOM, NIfTI)
2. **Property Definition:** Write spatial logic formulas
3. **Model Checking:** Verify properties against image
4. **Result Analysis:** Examine satisfied/violated regions

**Example Use Cases:**
- **Lesion Detection:** Find connected high-intensity regions
- **Anatomical Validation:** Verify organ relationships
- **Quality Control:** Check image acquisition artifacts

### 4.4 VoxLogica vs. Traditional Methods

| Aspect | Traditional | VoxLogica |
|--------|-------------|-----------|
| Specification | Procedural code | Declarative logic |
| Verification | Testing | Formal proof |
| Interpretability | Code inspection | Logical reasoning |
| Flexibility | High | Medium |
| Correctness | Empirical | Mathematical |

---

## 5. The ISOLA24 Paper: "Towards Hybrid-AI in Imaging Using VoxLogicA" (20 minutes)

### 5.1 Paper Overview

**Publication Details:**
- **Title:** "Towards Hybrid-AI in Imaging Using VoxLogicA"
- **Authors:** Gina Belmonte, Laura Bussi, Vincenzo Ciancia, Diego Latella, Mieke Massink
- **Venue:** ISoLA 2024 (International Symposium on Leveraging Applications of Formal Methods)
- **Pages:** 205-221
- **DOI:** 10.1007/978-3-031-75387-9_13

### 5.2 Research Context and Significance

**ISOLA 2024 Focus:**
- Premier venue for bridging formal methods theory and practical applications
- Emphasis on real-world impact of formal verification techniques
- Platform for demonstrating innovative applications in critical domains

**Paper's Contribution to Hybrid AI:**
This paper represents a significant step toward integrating formal methods with AI in medical imaging, addressing the critical need for:
- **Interpretable AI:** Making AI decisions explainable to medical professionals
- **Reliable automation:** Combining data-driven learning with domain knowledge
- **Clinical validation:** Providing mathematical guarantees for medical applications

### 5.3 Key Research Contributions

**Methodological Advances:**
- **Hybrid Architecture:** Novel integration of VoxLogica spatial model checking with machine learning pipelines
- **Spatial Logic Extensions:** New operators specifically designed for medical imaging applications
- **Performance Optimization:** Efficient algorithms for real-time medical image analysis

**Practical Applications:**
- **Medical Image Segmentation:** Combining CNN-based segmentation with formal geometric constraints
- **Quality Assurance:** Automated verification of imaging analysis results
- **Clinical Decision Support:** Providing explainable reasoning for diagnostic assistance

### 5.4 Hybrid AI Framework

**The VoxLogicA Approach:**
1. **ML Preprocessing:** Neural networks handle noise reduction and initial feature extraction
2. **Formal Specification:** Spatial logic defines anatomical and pathological constraints
3. **Model Checking:** VoxLogicA verifies that ML results satisfy medical requirements
4. **Hybrid Validation:** Combined confidence from both statistical and logical reasoning

**Example Workflow:**
```
Medical Image → CNN Segmentation → VoxLogicA Verification → Validated Results
                     ↓                        ↓
              Statistical Confidence    Logical Certainty
                     ↓                        ↓
                    Combined Hybrid Confidence Score
```

### 5.5 Clinical Impact and Future Directions

**Immediate Benefits:**
- **Increased Trust:** Medical professionals can understand and verify AI decisions
- **Reduced Errors:** Formal constraints catch ML mistakes that violate medical knowledge
- **Regulatory Compliance:** Mathematical verification supports medical device approval

**Future Research Directions:**
- **Scalability:** Extending to larger, more complex medical imaging datasets
- **Real-time Processing:** Optimizing for clinical workflow integration
- **Multi-modal Integration:** Combining different imaging modalities with unified formal specifications

---

## 6. Recent Advances: Medical Imaging Applications (15 minutes)

### 6.1 Contemporary Research in Medical Imaging

**Recent Work by Course Instructor:**
Building on the theoretical foundations established in previous work, recent research has focused on practical applications of formal methods in clinical medical imaging scenarios.

**Key Research Areas:**
- **Clinical Validation:** Real-world testing of VoxLogica in hospital environments
- **Multi-modal Integration:** Combining MRI, CT, and ultrasound data analysis
- **Performance Optimization:** Scaling formal methods for large medical datasets
- **Regulatory Compliance:** Meeting FDA and CE marking requirements for medical AI

### 6.2 Practical Applications in Medicine

**Current Medical Imaging Challenges:**
- **Diagnostic Accuracy:** Reducing false positives and negatives in automated analysis
- **Workflow Integration:** Seamlessly incorporating AI tools into clinical practice
- **Interpretability Requirements:** Meeting regulatory demands for explainable AI
- **Multi-institutional Validation:** Ensuring methods work across different hospitals and equipment

**Formal Methods Solutions:**
- **Spatial Logic Specifications:** Encoding medical knowledge as verifiable constraints
- **Hybrid Validation:** Combining statistical and logical confidence measures
- **Quality Assurance:** Automated detection of analysis errors and artifacts
- **Documentation:** Providing audit trails for regulatory compliance

### 6.3 Impact on Medical Practice

**Clinical Benefits:**
- **Enhanced Diagnostic Confidence:** Doctors can verify AI reasoning
- **Reduced Training Time:** Formal specifications capture expert knowledge
- **Standardization:** Consistent analysis across different institutions
- **Risk Mitigation:** Mathematical guarantees reduce liability concerns

**Research Contributions:**
- **Methodological Advances:** New spatial operators for medical imaging
- **Performance Studies:** Comparative analysis of hybrid vs. pure ML approaches
- **Clinical Validation:** Real-world testing in medical environments
- **Tool Development:** User-friendly interfaces for medical professionals

---

## 7. Ethics and Human-Centric AI in Medical Imaging (20 minutes)

### 6.1 Ethical Considerations

**Key Principles:**
- **Transparency:** AI decisions must be explainable to medical professionals
- **Accountability:** Clear responsibility for AI-assisted diagnoses
- **Fairness:** Avoiding bias in training data and algorithms
- **Privacy:** Protecting patient data and medical information

### 6.2 The Human-Centric Approach

**Human-in-the-Loop:**
- AI assists but doesn't replace medical expertise
- Doctors maintain final decision authority
- Continuous feedback improves system performance

**Hybrid AI Benefits:**
- **Interpretability:** Formal methods provide clear reasoning
- **Validation:** Multiple approaches increase confidence
- **Flexibility:** Adapts to different clinical workflows
- **Trust:** Transparent processes build user confidence

### 6.3 Regulatory and Professional Considerations

**Medical Device Regulation:**
- AI systems must meet safety and efficacy standards
- Formal verification can support regulatory approval
- Documentation and traceability requirements

**Professional Standards:**
- Integration with existing clinical workflows
- Training requirements for medical professionals
- Quality assurance and continuous monitoring

---

## 8. Course Preview and Next Steps (10 minutes)

### 7.1 Course Journey

**Weeks 1-4:** Foundations
- Image generation and preprocessing
- Traditional image processing
- Programming with ITK/SimpleITK

**Weeks 5-8:** Formal Methods
- Deep dive into VoxLogica
- Spatial logic programming
- Case studies and applications

**Weeks 9-12:** Hybrid Approaches
- Machine learning integration
- Performance evaluation
- Real-world applications

### 7.2 Learning Approach

**Theory + Practice:**
- Conceptual understanding of methods
- Hands-on programming exercises
- Real medical imaging datasets

**Progressive Complexity:**
- Start with basic concepts
- Build to sophisticated hybrid systems
- Culminate in individual projects

---

## Summary and Key Takeaways

1. **Hybrid AI** combines symbolic and subsymbolic approaches for robust medical imaging solutions
2. **Formal methods** provide mathematical precision and verification capabilities
3. **VoxLogica** enables declarative specification of spatial properties in medical images
4. **Ethics and transparency** are crucial in medical AI applications
5. **Integration** of multiple approaches addresses individual method limitations

---

## Preparation for Next Lecture

**Reading:**
- Review basic concepts of medical imaging modalities
- Familiarize yourself with Python programming basics
- Install required software (instructions will be provided)

**Questions to Consider:**
- How might formal verification improve trust in medical AI?
- What spatial relationships are important in your area of medical interest?
- How can we balance automation with human expertise in medical imaging?

---

## References and Further Reading

1. **Belmonte, G., Bussi, L., Ciancia, V., Latella, D., Massink, M.** (2024). "Towards Hybrid-AI in Imaging Using VoxLogicA." *ISoLA 2024: Leveraging Applications of Formal Methods*, pp. 205-221. DOI: 10.1007/978-3-031-75387-9_13

2. **Ciancia, V., et al.** (2024). "[Recent Medical Imaging Paper Title]." *[Medical Imaging Journal]*, [Volume], [Pages]. DOI: [DOI] 
   *Note: Please update with specific details of your recent medical imaging publication*

3. **Ciancia, V., Latella, D., Loreti, M., Massink, M.** (2014). "Specifying and verifying properties of space." *Theoretical Computer Science*, 550, 25-41.

3. **Nenzi, L., Bortolussi, L., Ciancia, V., Loreti, M., Massink, M.** (2015). "Qualitative and quantitative monitoring of spatio-temporal properties." *Runtime Verification*, pp. 21-37.

4. **Bartocci, E., Bortolussi, L., Loreti, M., Nenzi, L.** (2018). "Monitoring mobile and spatially distributed cyber-physical systems." *ACM Computing Surveys*, 51(4), 1-29.

5. **Medical Imaging Ethics Guidelines:** IEEE Standards for Medical Device Software, FDA Guidelines for AI/ML-Based Medical Devices

6. **VoxLogicA Tool and Documentation:** Available at the official VoxLogicA repository and ISTI-CNR research pages

7. **Recent Advances in Hybrid AI:** Survey papers on neuro-symbolic AI and explainable AI in healthcare applications