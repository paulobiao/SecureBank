"""
statistical_analysis.py

Módulo de análise estatística rigorosa para validação científica do SecureBank™.
Implementa testes de hipótese, intervalos de confiança e tamanho de efeito
para publicação em periódicos de alto impacto (Q1).

Autor: SecureBank Research Team
Data: 2025-12-12
"""

from typing import List, Dict, Tuple, Optional
import numpy as np
from scipy import stats
from dataclasses import dataclass
import warnings


@dataclass
class StatisticalTestResult:
    """
    Resultado de um teste estatístico completo.
    """
    test_name: str
    statistic: float
    p_value: float
    is_significant: bool
    alpha: float
    effect_size: Optional[float] = None
    effect_size_interpretation: Optional[str] = None
    confidence_interval: Optional[Tuple[float, float]] = None
    baseline_mean: Optional[float] = None
    securebank_mean: Optional[float] = None
    baseline_std: Optional[float] = None
    securebank_std: Optional[float] = None
    sample_size: Optional[int] = None
    normality_baseline: Optional[bool] = None
    normality_securebank: Optional[bool] = None


def test_normality(data: List[float], alpha: float = 0.05) -> Tuple[bool, float]:
    """
    Testa normalidade usando Shapiro-Wilk test.
    
    Args:
        data: Lista de valores numéricos
        alpha: Nível de significância (default: 0.05)
    
    Returns:
        (is_normal, p_value): Tupla com resultado booleano e p-value
    
    References:
        Shapiro, S. S., & Wilk, M. B. (1965). An analysis of variance test 
        for normality (complete samples). Biometrika, 52(3/4), 591-611.
    """
    if len(data) < 3:
        warnings.warn("Shapiro-Wilk test requires at least 3 samples")
        return False, 1.0
    
    statistic, p_value = stats.shapiro(data)
    is_normal = p_value > alpha
    
    return is_normal, p_value


def welch_t_test(
    baseline: List[float], 
    securebank: List[float], 
    alpha: float = 0.05,
    alternative: str = 'two-sided'
) -> StatisticalTestResult:
    """
    Realiza teste t de Welch (para variâncias desiguais).
    
    O teste de Welch é mais robusto que o t-test tradicional quando
    as variâncias das duas amostras são diferentes.
    
    Args:
        baseline: Dados da arquitetura baseline
        securebank: Dados da arquitetura SecureBank™
        alpha: Nível de significância
        alternative: 'two-sided', 'less', ou 'greater'
    
    Returns:
        StatisticalTestResult com resultados completos
    
    References:
        Welch, B. L. (1947). The generalization of "Student's" problem when 
        several different population variances are involved. Biometrika, 
        34(1-2), 28-35.
    """
    baseline_arr = np.array(baseline)
    securebank_arr = np.array(securebank)
    
    # Estatísticas descritivas
    baseline_mean = np.mean(baseline_arr)
    baseline_std = np.std(baseline_arr, ddof=1)
    securebank_mean = np.mean(securebank_arr)
    securebank_std = np.std(securebank_arr, ddof=1)
    
    # Teste t de Welch
    statistic, p_value = stats.ttest_ind(
        baseline_arr, 
        securebank_arr, 
        equal_var=False,
        alternative=alternative
    )
    
    # Cohen's d (tamanho de efeito)
    pooled_std = np.sqrt((baseline_std**2 + securebank_std**2) / 2)
    cohens_d = (securebank_mean - baseline_mean) / pooled_std if pooled_std > 0 else 0.0
    effect_interpretation = interpret_cohens_d(cohens_d)
    
    # Intervalo de confiança 95% para a diferença de médias
    ci = confidence_interval_difference(baseline_arr, securebank_arr, confidence=0.95)
    
    # Testes de normalidade
    norm_baseline, _ = test_normality(baseline)
    norm_securebank, _ = test_normality(securebank)
    
    return StatisticalTestResult(
        test_name="Welch's t-test",
        statistic=statistic,
        p_value=p_value,
        is_significant=(p_value < alpha),
        alpha=alpha,
        effect_size=cohens_d,
        effect_size_interpretation=effect_interpretation,
        confidence_interval=ci,
        baseline_mean=baseline_mean,
        securebank_mean=securebank_mean,
        baseline_std=baseline_std,
        securebank_std=securebank_std,
        sample_size=len(baseline),
        normality_baseline=norm_baseline,
        normality_securebank=norm_securebank
    )


def mann_whitney_u_test(
    baseline: List[float], 
    securebank: List[float], 
    alpha: float = 0.05,
    alternative: str = 'two-sided'
) -> StatisticalTestResult:
    """
    Realiza teste Mann-Whitney U (teste não-paramétrico).
    
    Usado quando os dados não seguem distribuição normal.
    Testa se duas amostras independentes vêm da mesma distribuição.
    
    Args:
        baseline: Dados da arquitetura baseline
        securebank: Dados da arquitetura SecureBank™
        alpha: Nível de significância
        alternative: 'two-sided', 'less', ou 'greater'
    
    Returns:
        StatisticalTestResult com resultados completos
    
    References:
        Mann, H. B., & Whitney, D. R. (1947). On a test of whether one of 
        two random variables is stochastically larger than the other. 
        The Annals of Mathematical Statistics, 18(1), 50-60.
    """
    baseline_arr = np.array(baseline)
    securebank_arr = np.array(securebank)
    
    # Estatísticas descritivas
    baseline_mean = np.mean(baseline_arr)
    baseline_std = np.std(baseline_arr, ddof=1)
    securebank_mean = np.mean(securebank_arr)
    securebank_std = np.std(securebank_arr, ddof=1)
    
    # Teste Mann-Whitney U
    statistic, p_value = stats.mannwhitneyu(
        baseline_arr, 
        securebank_arr, 
        alternative=alternative
    )
    
    # Rank-biserial correlation (tamanho de efeito para Mann-Whitney)
    n1 = len(baseline_arr)
    n2 = len(securebank_arr)
    rank_biserial = 1 - (2*statistic) / (n1 * n2)
    effect_interpretation = interpret_rank_biserial(rank_biserial)
    
    # Intervalo de confiança 95% para a diferença de médias
    ci = confidence_interval_difference(baseline_arr, securebank_arr, confidence=0.95)
    
    # Testes de normalidade
    norm_baseline, _ = test_normality(baseline)
    norm_securebank, _ = test_normality(securebank)
    
    return StatisticalTestResult(
        test_name="Mann-Whitney U test",
        statistic=statistic,
        p_value=p_value,
        is_significant=(p_value < alpha),
        alpha=alpha,
        effect_size=rank_biserial,
        effect_size_interpretation=effect_interpretation,
        confidence_interval=ci,
        baseline_mean=baseline_mean,
        securebank_mean=securebank_mean,
        baseline_std=baseline_std,
        securebank_std=securebank_std,
        sample_size=len(baseline),
        normality_baseline=norm_baseline,
        normality_securebank=norm_securebank
    )


def cohens_d(baseline: List[float], securebank: List[float]) -> float:
    """
    Calcula Cohen's d (tamanho de efeito).
    
    Cohen's d é uma medida padronizada da diferença entre duas médias,
    expressa em unidades de desvio padrão.
    
    Args:
        baseline: Dados da arquitetura baseline
        securebank: Dados da arquitetura SecureBank™
    
    Returns:
        Valor de Cohen's d
    
    References:
        Cohen, J. (1988). Statistical power analysis for the behavioral 
        sciences (2nd ed.). Hillsdale, NJ: Lawrence Erlbaum Associates.
    """
    baseline_arr = np.array(baseline)
    securebank_arr = np.array(securebank)
    
    mean_diff = np.mean(securebank_arr) - np.mean(baseline_arr)
    pooled_std = np.sqrt(
        (np.std(baseline_arr, ddof=1)**2 + np.std(securebank_arr, ddof=1)**2) / 2
    )
    
    return mean_diff / pooled_std if pooled_std > 0 else 0.0


def interpret_cohens_d(d: float) -> str:
    """
    Interpreta o valor de Cohen's d segundo convenções estabelecidas.
    
    Args:
        d: Valor de Cohen's d
    
    Returns:
        Interpretação textual do tamanho de efeito
    
    References:
        Cohen, J. (1988). Statistical power analysis for the behavioral 
        sciences (2nd ed.). Hillsdale, NJ: Lawrence Erlbaum Associates.
        
        Sawilowsky, S. S. (2009). New effect size rules of thumb. 
        Journal of Modern Applied Statistical Methods, 8(2), 597-599.
    """
    abs_d = abs(d)
    
    if abs_d < 0.2:
        return "negligible"
    elif abs_d < 0.5:
        return "small"
    elif abs_d < 0.8:
        return "medium"
    elif abs_d < 1.2:
        return "large"
    elif abs_d < 2.0:
        return "very large"
    else:
        return "huge"


def interpret_rank_biserial(r: float) -> str:
    """
    Interpreta rank-biserial correlation (tamanho de efeito para Mann-Whitney).
    
    Args:
        r: Valor de rank-biserial correlation
    
    Returns:
        Interpretação textual do tamanho de efeito
    """
    abs_r = abs(r)
    
    if abs_r < 0.1:
        return "negligible"
    elif abs_r < 0.3:
        return "small"
    elif abs_r < 0.5:
        return "medium"
    elif abs_r < 0.7:
        return "large"
    else:
        return "very large"


def confidence_interval_difference(
    baseline: np.ndarray, 
    securebank: np.ndarray, 
    confidence: float = 0.95
) -> Tuple[float, float]:
    """
    Calcula intervalo de confiança para a diferença de médias.
    
    Args:
        baseline: Array com dados baseline
        securebank: Array com dados SecureBank™
        confidence: Nível de confiança (default: 0.95)
    
    Returns:
        (lower, upper): Tupla com limites inferior e superior do IC
    """
    mean_diff = np.mean(securebank) - np.mean(baseline)
    
    # Erro padrão da diferença
    n1 = len(baseline)
    n2 = len(securebank)
    s1 = np.std(baseline, ddof=1)
    s2 = np.std(securebank, ddof=1)
    
    se_diff = np.sqrt((s1**2 / n1) + (s2**2 / n2))
    
    # Graus de liberdade (aproximação de Welch)
    df = ((s1**2 / n1) + (s2**2 / n2))**2 / (
        (s1**2 / n1)**2 / (n1 - 1) + (s2**2 / n2)**2 / (n2 - 1)
    )
    
    # Valor crítico t
    alpha = 1 - confidence
    t_critical = stats.t.ppf(1 - alpha/2, df)
    
    margin = t_critical * se_diff
    
    return (mean_diff - margin, mean_diff + margin)


def bonferroni_correction(alpha: float, num_comparisons: int) -> float:
    """
    Aplica correção de Bonferroni para múltiplas comparações.
    
    A correção de Bonferroni controla a taxa de erro do tipo I (falsos positivos)
    ao realizar múltiplos testes de hipótese.
    
    Args:
        alpha: Nível de significância original
        num_comparisons: Número de comparações sendo realizadas
    
    Returns:
        Alpha ajustado para múltiplas comparações
    
    References:
        Bonferroni, C. E. (1936). Teoria statistica delle classi e calcolo 
        delle probabilità. Pubblicazioni del R Istituto Superiore di Scienze 
        Economiche e Commerciali di Firenze, 8, 3-62.
    """
    return alpha / num_comparisons


def choose_test_automatically(
    baseline: List[float], 
    securebank: List[float], 
    alpha: float = 0.05,
    alternative: str = 'two-sided'
) -> StatisticalTestResult:
    """
    Escolhe automaticamente o teste estatístico apropriado.
    
    Estratégia:
    1. Testa normalidade de ambas as amostras (Shapiro-Wilk)
    2. Se ambas são normais: usa Welch's t-test
    3. Se pelo menos uma não é normal: usa Mann-Whitney U test
    
    Args:
        baseline: Dados da arquitetura baseline
        securebank: Dados da arquitetura SecureBank™
        alpha: Nível de significância
        alternative: 'two-sided', 'less', ou 'greater'
    
    Returns:
        StatisticalTestResult com o teste apropriado
    """
    # Testa normalidade
    norm_baseline, p_baseline = test_normality(baseline, alpha)
    norm_securebank, p_securebank = test_normality(securebank, alpha)
    
    # Escolhe teste apropriado
    if norm_baseline and norm_securebank:
        # Ambos normais: usa Welch's t-test (paramétrico)
        result = welch_t_test(baseline, securebank, alpha, alternative)
    else:
        # Pelo menos um não-normal: usa Mann-Whitney (não-paramétrico)
        result = mann_whitney_u_test(baseline, securebank, alpha, alternative)
    
    return result


def significance_stars(p_value: float) -> str:
    """
    Retorna a notação de estrelas para significância estatística.
    
    Args:
        p_value: P-value do teste
    
    Returns:
        String com estrelas: '***' (p<0.001), '**' (p<0.01), '*' (p<0.05), 'ns' (não significante)
    """
    if p_value < 0.001:
        return "***"
    elif p_value < 0.01:
        return "**"
    elif p_value < 0.05:
        return "*"
    else:
        return "ns"


def format_p_value(p_value: float) -> str:
    """
    Formata p-value para exibição em publicações científicas.
    
    Args:
        p_value: P-value do teste
    
    Returns:
        String formatada (ex: "p < 0.001" ou "p = 0.023")
    """
    if p_value < 0.001:
        return "p < 0.001"
    else:
        return f"p = {p_value:.3f}"


def format_confidence_interval(ci: Tuple[float, float], precision: int = 3) -> str:
    """
    Formata intervalo de confiança para exibição.
    
    Args:
        ci: Tupla (lower, upper) com os limites do IC
        precision: Número de casas decimais
    
    Returns:
        String formatada (ex: "95% CI [0.123, 0.456]")
    """
    return f"95% CI [{ci[0]:.{precision}f}, {ci[1]:.{precision}f}]"


def comprehensive_comparison(
    baseline_data: Dict[str, List[float]],
    securebank_data: Dict[str, List[float]],
    alpha: float = 0.05,
    bonferroni: bool = True
) -> Dict[str, StatisticalTestResult]:
    """
    Realiza comparação estatística abrangente entre baseline e SecureBank™.
    
    Para cada métrica (TII, SAE, ITAL):
    - Escolhe teste apropriado automaticamente
    - Aplica correção de Bonferroni se solicitado
    - Retorna resultados completos
    
    Args:
        baseline_data: Dict com métricas baseline {"TII": [...], "SAE": [...], "ITAL": [...]}
        securebank_data: Dict com métricas SecureBank™ {"TII": [...], "SAE": [...], "ITAL": [...]}
        alpha: Nível de significância base
        bonferroni: Se True, aplica correção de Bonferroni
    
    Returns:
        Dict com resultados para cada métrica
    """
    metrics = list(baseline_data.keys())
    num_comparisons = len(metrics)
    
    # Ajusta alpha se correção de Bonferroni for solicitada
    adjusted_alpha = bonferroni_correction(alpha, num_comparisons) if bonferroni else alpha
    
    results = {}
    
    for metric in metrics:
        baseline = baseline_data[metric]
        securebank = securebank_data[metric]
        
        # Escolhe teste apropriado automaticamente
        result = choose_test_automatically(
            baseline, 
            securebank, 
            alpha=adjusted_alpha,
            alternative='two-sided'
        )
        
        results[metric] = result
    
    return results


def generate_markdown_table(results: Dict[str, StatisticalTestResult]) -> str:
    """
    Gera tabela Markdown formatada com resultados estatísticos.
    
    Args:
        results: Dict com StatisticalTestResult para cada métrica
    
    Returns:
        String com tabela Markdown formatada
    """
    lines = []
    lines.append("| Metric | Baseline (M±SD) | SecureBank™ (M±SD) | Test | Statistic | p-value | Sig. | Effect Size | Interpretation | 95% CI |")
    lines.append("|--------|-----------------|---------------------|------|-----------|---------|------|-------------|----------------|--------|")
    
    for metric, result in results.items():
        baseline_str = f"{result.baseline_mean:.3f}±{result.baseline_std:.3f}"
        securebank_str = f"{result.securebank_mean:.3f}±{result.securebank_std:.3f}"
        test_abbr = "Welch-t" if "Welch" in result.test_name else "Mann-W"
        stat_str = f"{result.statistic:.3f}"
        p_str = format_p_value(result.p_value)
        sig_str = significance_stars(result.p_value)
        effect_str = f"{result.effect_size:.3f}" if result.effect_size else "N/A"
        interp_str = result.effect_size_interpretation or "N/A"
        ci_str = f"[{result.confidence_interval[0]:.3f}, {result.confidence_interval[1]:.3f}]" if result.confidence_interval else "N/A"
        
        lines.append(f"| {metric} | {baseline_str} | {securebank_str} | {test_abbr} | {stat_str} | {p_str} | {sig_str} | {effect_str} | {interp_str} | {ci_str} |")
    
    return "\n".join(lines)


def generate_latex_table(results: Dict[str, StatisticalTestResult]) -> str:
    """
    Gera tabela LaTeX formatada com resultados estatísticos.
    
    Args:
        results: Dict com StatisticalTestResult para cada métrica
    
    Returns:
        String com tabela LaTeX formatada
    """
    lines = []
    lines.append("\\begin{table}[htbp]")
    lines.append("\\centering")
    lines.append("\\caption{Statistical Comparison: Baseline vs. SecureBank™}")
    lines.append("\\label{tab:statistical_results}")
    lines.append("\\begin{tabular}{lccccccc}")
    lines.append("\\toprule")
    lines.append("Metric & Baseline & SecureBank™ & Test & p-value & Sig. & Cohen's d & 95\\% CI \\\\")
    lines.append("       & (M±SD)   & (M±SD)      &      &         &      &           &         \\\\")
    lines.append("\\midrule")
    
    for metric, result in results.items():
        baseline_str = f"{result.baseline_mean:.3f}±{result.baseline_std:.3f}"
        securebank_str = f"{result.securebank_mean:.3f}±{result.securebank_std:.3f}"
        test_abbr = "Welch" if "Welch" in result.test_name else "Mann-W"
        p_str = format_p_value(result.p_value)
        sig_str = significance_stars(result.p_value)
        effect_str = f"{result.effect_size:.3f}" if result.effect_size else "---"
        ci_str = f"[{result.confidence_interval[0]:.3f}, {result.confidence_interval[1]:.3f}]" if result.confidence_interval else "---"
        
        lines.append(f"{metric} & {baseline_str} & {securebank_str} & {test_abbr} & {p_str} & {sig_str} & {effect_str} & {ci_str} \\\\")
    
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    lines.append("\\end{table}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Exemplo de uso
    print("Statistical Analysis Module for SecureBank™")
    print("=" * 60)
    
    # Dados sintéticos para demonstração
    baseline_tii = [0.75 + np.random.normal(0, 0.05) for _ in range(30)]
    securebank_tii = [0.88 + np.random.normal(0, 0.04) for _ in range(30)]
    
    # Teste automático
    result = choose_test_automatically(baseline_tii, securebank_tii)
    
    print(f"\nTest: {result.test_name}")
    print(f"Baseline: {result.baseline_mean:.3f} ± {result.baseline_std:.3f}")
    print(f"SecureBank™: {result.securebank_mean:.3f} ± {result.securebank_std:.3f}")
    print(f"p-value: {format_p_value(result.p_value)}")
    print(f"Significance: {significance_stars(result.p_value)}")
    print(f"Effect size: {result.effect_size:.3f} ({result.effect_size_interpretation})")
    print(f"95% CI: {format_confidence_interval(result.confidence_interval)}")
