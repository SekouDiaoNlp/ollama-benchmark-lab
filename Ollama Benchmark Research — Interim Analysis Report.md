# 📊 Ollama Benchmark Research — Interim Analysis Report

## 🧠 1. Executive Summary

This benchmark primarily measures **latency** and **output verbosity**, not correctness. Despite that limitation, strong and consistent patterns emerge across model families.

### Key findings:

- **Prompting strategy dominates model size** (PLAN vs ACT has larger impact than parameter count in many cases)
- **7B models cluster into three clear regimes**: fast/efficient, balanced, and slow/verbose
- **Some models show extreme instability**, indicating sensitivity to sampling or prompt structure
- **Codellama 7B (acting variant)** is the most reliable general-purpose engineering model in this dataset
- **Qwen models are the most expressive but also the most inefficient**

---

## ⚙️ 2. What was measured

Each run records:

- **Latency (seconds)** → execution + generation time
- **Output size (characters)** → proxy for token usage / verbosity
- **Mode**
  - `PLAN` → reasoning-heavy prompt
  - `ACT` → execution-oriented prompt
- **Prompt style**
  - `acting`, `planning`, `general`, `noyap`

⚠️ Important: **No correctness evaluation is included yet**.

---

## 📈 3. Model Behavior Clusters

### 🟢 Cluster A — Fast & Efficient Models

| Models |
|--------|
| starcoder2:7b |
| starcoder2:3b |
| granite-code:3b |

### Characteristics
- Very low latency
- Small outputs
- Stable execution
- Weak reasoning depth

### Interpretation
These are **production-speed tools**, not reasoning engines.

---

### 🟡 Cluster B — Balanced Engineering Models (BEST OVERALL)

| Models |
|--------|
| codellama:7b-instruct |
| qwen2.5-coder:7b |
| mistral:7b-instruct |

### Characteristics
- Good balance of speed and verbosity
- Stable outputs
- Consistent PLAN/ACT separation
- Reasonable token efficiency

### Interpretation
These are the **best candidates for real SWE-style agents**.

---

### 🔴 Cluster C — Heavy Reasoning / Over-Verbose Models

| Models |
|--------|
| qwen2.5:7b |
| phi3:medium |
| codegemma:7b |

### Characteristics
- Very large outputs
- High latency
- High variance
- Often redundant reasoning

### Interpretation
These models **over-generate rather than optimize reasoning quality**.

---

## ⚖️ 4. PLAN vs ACT Effectiveness

### Key observation:
> Prompting strategy has a larger effect than model size.

#### Example: codellama 7B
- ACT mode improves execution consistency
- PLAN mode increases reasoning depth but also latency

#### Example: qwen2.5-coder:7b
- ACT dramatically reduces verbosity
- PLAN is highly unstable and sometimes over-verbose

### Conclusion:
Prompt design is a **first-class performance lever**.

---

## 📉 5. Stability Analysis

### High variance models

| Model | Behavior |
|------|--------|
| qwen2.5-coder:7b | extreme latency variance |
| phi3:medium | corrupted / inconsistent runs |
| codegemma:7b | inconsistent verbosity |

### Interpretation
These models are **sensitive to sampling + prompt structure**, making them unreliable for benchmarking without normalization.

---

## 🚨 6. Data Quality Issues Observed

### 1. Sleep interruption corruption
- Some runs (phi3:medium) are invalid due to system sleep
- Results must be flagged or discarded

### 2. Terminal artifacts in logs
- Spinner characters (`⠋⠙⠸`) pollute output logs
- Requires cleaning layer

### 3. Missing correctness signal
- Output size is not a proxy for correctness

---

## 🏆 7. Current Best Models (based on this benchmark)

### 🥇 Best overall engineering model
**codellama:7b-instruct-acting-noyap**
- Best balance of:
  - speed
  - stability
  - PLAN/ACT consistency

---

### 🥈 Best fast execution model
**starcoder2:7b-acting-noyap**
- Extremely fast
- Low overhead
- Good for real-time tasks

---

### 🥉 Best reasoning-heavy model (but inefficient)
**qwen2.5:7b**
- Strong reasoning depth
- Very verbose
- High compute cost

---

## 📊 8. Key Insights (Research-Level)

### Insight 1 — Prompting dominates architecture
A well-designed "acting" prompt can outperform a larger model with a poor prompt.

---

### Insight 2 — Verbosity ≠ reasoning quality
Large outputs often reflect:
- repetition
- self-checking loops
- verbosity bias

---

### Insight 3 — SWE agents need structure, not size
Best-performing models are those that:
- follow instructions strictly
- minimize unnecessary reasoning
- produce stable outputs

---

## 🧠 9. Implications for Next Version of Benchmark

### Must add:

#### ✔ Correctness evaluation
- AST validation
- unit tests
- hidden test suite (SWE-bench style)

#### ✔ Stability metrics
- variance per task
- failure clustering

#### ✔ Normalization layer
- strip ANSI artifacts
- clean streaming output

#### ✔ True performance frontier
- latency vs correctness
- verbosity vs correctness

---

## 🚀 10. Strategic Conclusion

This benchmark already reveals a key principle:

> The best SWE-style model is not the largest one — it is the one that best follows structured execution prompts under constraint.

Currently:

- **Codellama 7B = best engineering baseline**
- **Starcoder2 = fastest execution layer**
- **Qwen models = strongest reasoning but inefficient**

---

## Next milestone recommendation

The next iteration should transition from:

> ❌ “behavior benchmarking”

to:

> ✅ “correctness + SWE-bench-style patch validation system”

This is where model rankings will become truly meaningful.