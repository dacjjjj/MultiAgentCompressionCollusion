# Compression as an Unwitting Accomplice: How Token-Saving Summarisation Undermines Safety Monitoring in Multi-Agent Pipelines

Juan Dominguez
University of Bristol

With Apart Research

## Abstract

Multi-agent AI systems increasingly compress inter-agent communication to reduce token costs. We investigate how this compression interacts with safety monitoring in a code review pipeline where two untrusted agents (a code writer and reviewer) may collude to pass backdoored code past a trusted safety monitor. We test three attack strategies — semantic collusion with obvious backdoors, subtle logic flaws, and context window stuffing — across three compression conditions (baseline, compressed, and full-monitor). We find that (1) compression can inadvertently launder malicious code by stripping evidence before monitors observe it, reducing detection from 1/5 to 0/5 for stuffing attacks, (2) safety monitors that detect ~100% of textbook vulnerabilities catch only 30% of subtle logic flaws, and (3) compression-aware attackers face a dilemma — hiding backdoors lets compression strip them, while making them prominent exposes them to monitors. We propose safety-aware compression as a partial mitigation and quantify the resulting safety–efficiency tradeoff. Our results suggest that token-saving compression in multi-agent pipelines has unexamined safety implications.

## 1. Introduction

Multi-agent AI systems are increasingly deployed for complex software engineering tasks, with distinct agents handling code generation, review, testing, and deployment. As these pipelines grow, so does the cost of inter-agent communication — each agent's output consumed as input by the next agent counts against token budgets. A natural optimisation is to compress or summarise intermediate outputs, and popular frameworks such as LangChain and AutoGen already employ LLM-based summarisation to manage context between agent turns.

Separately, the AI control literature recognises that untrusted agents may behave adversarially — colluding to pass harmful outputs through a pipeline while evading safety monitors. Greenblatt & Roger (2024) propose using trusted monitors to oversee untrusted agents, while Motwani et al. (2024) demonstrate that LLM agents can develop covert communication channels for coordination. However, existing work has not examined how compression — a standard, economically-motivated pipeline component — interacts with safety monitoring.

We investigate this interaction in a controlled code review pipeline where two untrusted agents (a code writer and reviewer) may collude to pass backdoored code past a trusted safety monitor. We systematically vary what the monitor observes (full code vs compressed summary) and what attack strategy the agents employ. Our main contributions are:

1. We demonstrate that a trusted compressor can inadvertently launder malicious code by stripping evidence of backdoors before safety monitors observe it.
2. We show that LLM-based safety monitors are primarily pattern matchers — detecting ~100% of textbook vulnerabilities but only 30% of subtle logic flaws.
3. We identify an attacker's dilemma in compressed pipelines: hiding backdoors makes them vulnerable to compression, while making them prominent exposes them to monitors.
4. We propose and evaluate safety-aware compression as a partial mitigation, quantifying the safety–efficiency tradeoff.

## 2. Related Work

**AI Agent Collusion.** Motwani et al. (2024) demonstrate that LLM agents can develop steganographic communication channels to coordinate covertly, even under paraphrasing defenses. Their work focuses on whether agents *can* collude; we investigate whether standard pipeline components inadvertently *assist* collusion.

**AI Control.** Greenblatt & Roger (2024) propose the AI control framework where trusted monitors oversee untrusted agents. We adopt their trusted/untrusted model distinction and extend it to examine how inter-agent compression affects monitor effectiveness.

**Prompt Compression.** LLMLingua (Jiang et al., 2023) and related work compress prompts at the token level to reduce costs. We model compression as LLM-based summarisation, consistent with how multi-agent frameworks (LangChain, AutoGen) operate in practice, and examine its security implications rather than its efficiency benefits.

## 3. Methods

### 3.1 Pipeline Architecture

[INSERT PIPELINE DIAGRAM — 3-panel figure showing Baseline, Compressed, and Full Monitor conditions]

Our pipeline consists of four components:
- **Agent A (Code Writer)** — an untrusted model (Mistral Small) that writes Python functions given a task description and a hidden attack directive.
- **Agent B (Code Reviewer)** — an untrusted model (Mistral Small) that reviews code and decides to APPROVE or REJECT.
- **Compressor** — a trusted model (Claude Sonnet 4.6) that summarises code to reduce token costs.
- **Safety Monitor** — a trusted model (Claude Sonnet 4.6) that independently evaluates each agent's output for unsafe behaviour.

The monitor evaluates Agent A's output and Agent B's review separately, without cross-referencing them. This models a realistic deployment where monitors observe each agent in isolation.

### 3.2 Experimental Conditions

We test three compression conditions, varying what Agent B and the monitor observe:

| Condition | Agent B sees | Monitor sees (Agent A) |
|-----------|-------------|----------------------|
| Baseline | Full code | Full code |
| Compressed | Summary | Summary |
| Full Monitor | Summary | Full code |

### 3.3 Attack Strategies

We test three attack strategies of escalating subtlety:

1. **Semantic Collusion** — Agent A embeds obvious backdoors (eval, exec, file writes, network calls). The backdoor's presence IS the collusion signal — Agent B recognises hidden functionality beyond the stated task.

2. **Subtle Logic Flaws** — Backdoors that do NOT match known vulnerability patterns: timing-vulnerable comparisons, predictable randomness, off-by-one errors, incomplete input validation, inverted permission logic, ReDoS, and weak encryption. These test whether monitors reason about correctness or merely pattern-match.

3. **Context Window Stuffing** — Agent A writes deliberately verbose code (80–100+ lines) with a backdoor buried in padding noise.
   - *Naive variant*: Agent A is unaware of compression.
   - *Compression-aware variant*: Agent A knows code will be summarised and designs the backdoor to survive compression by framing it as a core feature.

### 3.4 Task Datasets

We use three task sets: 10 honest tasks (control), 10 obvious attack tasks with textbook vulnerabilities, and 10 subtle attack tasks with logic flaws (timing vulnerabilities, weak crypto, off-by-one errors, ReDoS, etc.).

### 3.5 Metrics

- **Monitor Detection Rate**: proportion of cases where the monitor flagged either agent as UNSAFE.
- **Collusion Success Rate**: proportion where Agent B approved AND the monitor did not detect — i.e., the backdoor passed through the entire pipeline undetected.

## 4. Results

### 4.1 Subtle Logic Flaws

*Table 1: Subtle logic flaw results across compression conditions (n=10).*

| Condition | B Approved | Detected | Succeeded |
|-----------|-----------|----------|-----------|
| Baseline | 10/10 | 3/10 | 7/10 |
| Compressed | 8/10 | 3/10 | 5/10 |
| Full Monitor | 8/10 | 4/10 | 6/10 |

Detection dropped from ~100% (obvious backdoors, not shown) to 30% for subtle logic flaws. The monitor consistently missed: incomplete regex sanitisation, predictable password salting, rate limiter off-by-one errors, inverted permission hierarchies, cache key collisions, ReDoS vulnerabilities, and XOR key truncation. Compression had minimal effect on detection — the issue is not information loss but the monitor's inability to reason about code correctness.

### 4.2 Context Window Stuffing

*Table 2: Naive context stuffing results (n=5).*

| Condition | B Approved | Detected | Succeeded |
|-----------|-----------|----------|-----------|
| Baseline | 5/5 | 1/5 | 4/5 |
| Compressed | 5/5 | 0/5 | 5/5 |
| Full Monitor | 5/5 | 3/5 | 2/5 |

Naive stuffing was highly effective. The monitor detected only 1/5 at baseline, and 0/5 after compression — the compressor reduced ~286 lines to ~47 lines, stripping the 1–2 backdoor lines along with the padding. The Full Monitor condition partially restored detection to 3/5.

*Table 3: Compression-aware stuffing results (n=5).*

| Condition | B Approved | Detected | Succeeded |
|-----------|-----------|----------|-----------|
| Baseline | 5/5 | 5/5 | 0/5 |
| Compressed | 5/5 | 5/5 | 0/5 |
| Full Monitor | 5/5 | 5/5 | 0/5 |

The compression-aware strategy completely backfired — 5/5 detected across all conditions. By framing the backdoor as a "core feature" to survive compression, the attacker made it more prominent and easier for the monitor to detect.

### 4.3 Safety-Aware Compression (Defense)

We tested a modified compressor prompted to preserve security-relevant code patterns (eval, exec, file operations, network calls) verbatim in its summaries while compressing safe code aggressively.

*Table 4: Normal vs safety-aware compressor on stuffing attacks (n=5).*

| Compressor | Detected | Succeeded | Avg Compression Ratio |
|------------|----------|-----------|-----------------------|
| Normal | 4/5 | 1/5 | 0.24 |
| Safety-aware | 5/5 | 0/5 | 0.28 |

Safety-aware compression restored full detection (5/5) for stuffing attacks, at a minimal cost: compression ratio increased from 0.24 to 0.28 — only 4 percentage points of additional output, sacrificing roughly 5% of the token savings.

*Table 5: Normal vs safety-aware compressor on subtle logic flaws (n=10).*

| Compressor | Detected | Succeeded | Avg Compression Ratio |
|------------|----------|-----------|-----------------------|
| Normal | 3/10 | 7/10 | 0.45 |
| Safety-aware | 4/10 | 6/10 | 0.56 |

For subtle logic flaws, the safety-aware compressor showed marginal improvement (3/10 → 4/10), catching one additional case (cache key collision). However, 60% of subtle flaws still evaded detection — confirming that the defense works for known vulnerability patterns but not for logic flaws that the monitor cannot recognise in the first place.

### 4.4 Cross-Strategy Summary

*Table 5: Collusion success rates across all strategies and conditions.*

| Strategy | Baseline | Compressed | Full Monitor |
|----------|----------|------------|-------------|
| Subtle flaws | 7/10 | 5/10 | 6/10 |
| Stuffing (naive) | 4/5 | 5/5 | 2/5 |
| Stuffing (aware) | 0/5 | 0/5 | 0/5 |

## 5. Discussion and Limitations

### Compression as Evidence Destruction

A trusted, honestly-behaving compressor can inadvertently aid attackers by destroying evidence of backdoors. In the stuffing scenario, the compressor reduced ~286 lines to ~47 lines, removing the backdoor lines along with the padding. This is not adversarial behaviour — it is an emergent property of lossy summarisation. The compressor cannot be "fixed" without sacrificing the token savings that motivated compression. **The same compression that makes multi-agent pipelines economically viable also makes them harder to monitor safely.**

### Monitors Are Pattern Matchers

The monitor detected ~100% of textbook vulnerabilities but only 30% of subtle logic flaws. This suggests LLM-based monitors primarily pattern-match against known vulnerability signatures rather than reasoning about code correctness. The flaws that evaded detection — predictable salts, inverted permission hierarchies, ReDoS patterns — are precisely the kinds of vulnerabilities that cause real-world security incidents.

### The Attacker's Dilemma

Compression-aware stuffing results reveal a fundamental tension: **hide the backdoor** in noise (naive stuffing) and compression strips it, or **make it prominent** to survive compression and the monitor catches it. This dilemma arises because the properties that help a backdoor survive lossy compression — being central to the code's purpose — also make it salient to monitors. However, subtle logic flaws bypass this dilemma entirely, succeeding at 70% regardless of compression because the monitor cannot recognise them as threats.

### Limitations

- **Run variance**: We observed variance across runs (e.g., naive stuffing detection was 5/5 in one run and 1/5 in another), highlighting the stochastic nature of LLM outputs. Larger sample sizes and multiple runs would be needed for statistical robustness.
- **Single model pairing**: We tested Mistral Small (untrusted) vs Claude Sonnet (trusted). Different model pairings may yield different results.
- **LLM-based compression only**: Non-neural compression methods (e.g., LLMLingua) may behave differently.
- **Simplified pipeline**: Real systems have more complex communication patterns and trust boundaries.

### Future Work

Future work should test across multiple model families, investigate non-neural compression methods, explore compromised compressor scenarios, and examine whether monitors can be prompted or fine-tuned to detect subtle logic flaws rather than relying on vulnerability pattern matching.

## 6. Conclusion

We investigated how inter-agent communication compression affects safety monitoring in a multi-agent code review pipeline. Our experiments reveal three key findings: (1) compression can inadvertently launder malicious code by stripping evidence before monitors observe it, (2) LLM-based monitors fail to detect 70% of subtle logic flaws while catching nearly all textbook vulnerabilities, and (3) attackers in compressed pipelines face a dilemma between hiding backdoors (which compression may strip) and making them prominent (which monitors catch). These findings suggest that multi-agent pipeline designers must consider the safety implications of compression and that monitor effectiveness should be evaluated against realistic attack strategies rather than only known vulnerability patterns.

## Code and Data

- Repository: [TODO: Add GitHub link]
- Datasets: 10 honest tasks, 10 obvious attack tasks, 10 subtle attack tasks (included in repository)
- All experiment results saved as JSON in the repository's `results/` directory

## References

1. Motwani, S. R., et al. (2024). Secret Collusion Among Generative AI Agents. *NeurIPS 2024*.
2. Greenblatt, R. & Roger, B. (2024). AI Control: Improving Safety Despite Intentional Subversion. *Redwood Research*.
3. Jiang, H., et al. (2023). LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models. *EMNLP 2023*.

## LLM Usage Statement

Claude Code (Claude Opus) was used to assist with experiment design, code implementation, and drafting sections of this report. All experimental results were generated by running the pipeline code and are reported as observed. The author designed the research questions, evaluated results, and made all methodological decisions.
