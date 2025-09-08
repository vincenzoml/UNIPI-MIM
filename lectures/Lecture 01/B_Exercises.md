# Lecture 1: Practical Exercises

## Exercise 1: Conceptual Understanding (15 minutes)

### Part A: Method Classification
Classify the following medical imaging approaches as Symbolic, Subsymbolic, or Hybrid:

1. A CNN trained to segment brain tumors from MRI scans
2. A rule-based system that identifies lesions based on intensity thresholds and connectivity
3. A system that uses deep learning for initial segmentation, then applies geometric constraints to refine results
4. VoxLogica spatial model checking for anatomical structure validation
5. A radiomics pipeline that extracts features using mathematical formulas, then applies machine learning for classification

### Part B: Spatial Relationships
For a brain MRI scan, write natural language descriptions of spatial relationships that might be important for:

1. Tumor detection
2. Anatomical structure validation
3. Treatment planning
4. Quality control

**Example:** "The tumor should be a connected region with high intensity, located within brain tissue, and not overlapping with critical structures like the brainstem."

---

## Exercise 2: Introduction to Spatial Logic (20 minutes)

### Part A: Basic Formulas
Translate these natural language statements into pseudo-spatial logic:

1. "High-intensity regions that are connected"
2. "Areas within 5mm of the ventricles"
3. "Regions that are both high-intensity AND near the skull"
4. "Connected components that are NOT in the background"

### Part B: Medical Scenarios
Write spatial logic formulas for these medical imaging scenarios:

1. **Brain lesion detection:** Find connected regions with intensity above 200 that are within brain tissue
2. **Edema identification:** Find regions with medium intensity (100-180) that are near (within 8mm) of tumor regions
3. **Quality control:** Verify that skull regions surround brain tissue
4. **Anatomical validation:** Check that ventricles are connected and located in the center of the brain

**Template:**
```
property_name := condition1 AND/OR condition2 AND/OR spatial_operator(other_property, parameters)
```

---

## Exercise 3: Hybrid System Design (25 minutes)

### Scenario: Brain Tumor Segmentation Pipeline

You need to design a hybrid system for brain tumor segmentation that combines:
- Traditional image processing
- Machine learning
- Formal verification

### Part A: Pipeline Design
Design a 5-step pipeline that incorporates all three approaches. For each step, specify:
1. What method type (Traditional/ML/Formal)
2. What it does
3. Why it's needed at that stage

**Template:**
```
Step 1: [Method Type] - [Description] - [Justification]
Step 2: [Method Type] - [Description] - [Justification]
...
```

### Part B: Validation Strategy
How would you validate that your hybrid system is working correctly? Consider:
1. What could go wrong at each step?
2. How would formal methods help catch errors?
3. What metrics would you use?
4. How would you ensure clinical acceptance?

### Part C: Ethical Considerations
Identify potential ethical issues with your hybrid system and propose solutions:
1. Transparency and explainability
2. Bias and fairness
3. Privacy and data protection
4. Human oversight and control

---

## Exercise 4: VoxLogica Exploration (20 minutes)

### Part A: Tool Familiarization
If VoxLogica is available, explore the basic interface:
1. Load a sample medical image
2. Try basic intensity-based queries
3. Experiment with spatial operators
4. Visualize results

### Part B: Property Specification
Without running code, design VoxLogica queries for:

1. **Simple detection:**
   ```
   bright_regions := intensity > 150
   ```

2. **Connectivity constraint:**
   ```
   connected_bright := bright_regions AND connected(true)
   ```

3. **Spatial relationship:**
   ```
   near_center := near(center_point, 20)
   ```

4. **Complex combination:**
   ```
   candidate_lesion := connected_bright AND near_center AND size > 100
   ```

### Part C: Interpretation
For each query above, explain:
1. What medical structure or condition it might detect
2. What could cause false positives
3. What additional constraints might be needed
4. How it could be integrated with ML methods

---

## Exercise 5: Critical Thinking (15 minutes)

### Discussion Questions

1. **Limitations:** What are the main limitations of each approach (Traditional, ML, Formal) in medical imaging?

2. **Integration Challenges:** What technical and practical challenges might arise when combining different AI approaches?

3. **Clinical Adoption:** What factors would influence whether clinicians adopt a hybrid AI system?

4. **Future Directions:** How might hybrid AI in medical imaging evolve over the next 5-10 years?

### Reflection
Write a brief paragraph (100-150 words) on:
"How might hybrid AI change the role of medical imaging professionals?"

---

## Solutions and Discussion Points

### Exercise 1 Solutions:
**Part A:**
1. Subsymbolic (CNN)
2. Symbolic (rule-based)
3. Hybrid (ML + constraints)
4. Symbolic (formal methods)
5. Hybrid (mathematical + ML)

### Exercise 2 Sample Solutions:
**Part A:**
1. `high_intensity AND connected(true)`
2. `near(ventricles, 5)`
3. `high_intensity AND near(skull, distance)`
4. `connected(true) AND NOT background`

### Key Discussion Points:
- Balance between automation and human control
- Importance of interpretability in medical applications
- Challenges of integrating different methodological approaches
- Regulatory and ethical considerations in medical AI

---

## Homework Assignment

**Prepare for next lecture by:**
1. Installing Python and required libraries (instructions provided separately)
2. Reading about medical imaging modalities (MRI, CT, Ultrasound)
3. Thinking about a specific medical imaging problem you'd like to explore
4. Reviewing basic concepts of digital image processing

**Optional:** Research a recent paper on hybrid AI in medical imaging and prepare a 2-minute summary for class discussion.