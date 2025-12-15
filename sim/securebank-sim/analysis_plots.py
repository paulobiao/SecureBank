# analysis_plots.py
#
# Gera gráficos de análise adicionais a partir do último experimento,
# incluindo o gráfico de timeline com theta (trust score) e risco suavizados
# por média móvel, adequado para uso em artigo científico.

import json
from pathlib import Path

import matplotlib.pyplot as plt


# Raiz onde os experimentos são salvos pelo runner.py
EXPERIMENTS_ROOT = Path("experiments")


def get_latest_experiment_dir(root: Path = EXPERIMENTS_ROOT) -> Path:
    """
    Retorna o diretório de experimento mais recente (exp_YYYYMMDD_HHMMSS).

    Pressupõe que o runner.py cria subpastas em ./experiments
    com esse padrão de nome.
    """
    if not root.exists():
        raise RuntimeError(f"Nenhum diretório '{root}' encontrado.")

    exp_dirs = [p for p in root.iterdir() if p.is_dir() and p.name.startswith("exp_")]
    if not exp_dirs:
        raise RuntimeError("Nenhum experimento encontrado em ./experiments.")

    # Como os nomes têm timestamp no final, o "max" funciona bem
    latest = max(exp_dirs, key=lambda p: p.name)
    return latest


def load_timeline(exp_dir: Path) -> dict:
    """
    Carrega o arquivo timeline_run0.json gerado pela simulação.

    Esse arquivo deve conter, no mínimo:
    - "step"      : índice do evento
    - "sb_theta"  : trust score do SecureBank
    - "sb_risk"   : risco calculado para o SecureBank
    """
    timeline_path = exp_dir / "timeline_run0.json"
    if not timeline_path.exists():
        raise RuntimeError(f"Arquivo de timeline não encontrado: {timeline_path}")

    with timeline_path.open("r") as f:
        timeline = json.load(f)

    # Checagem mínima de campos esperados
    required_keys = ["step", "sb_theta", "sb_risk"]
    for k in required_keys:
        if k not in timeline:
            raise RuntimeError(f"Campo '{k}' ausente em {timeline_path}")

    return timeline


def rolling_average(values, window: int):
    """
    Calcula média móvel simples com janela deslizante.

    - values: sequência de valores (lista ou similar)
    - window: tamanho da janela (em número de eventos)

    Retorna uma lista do mesmo tamanho que 'values'.
    """
    if window <= 1:
        return list(values)

    out = []
    cumsum = 0.0
    for i, v in enumerate(values):
        cumsum += v
        if i >= window:
            cumsum -= values[i - window]
        out.append(cumsum / min(i + 1, window))
    return out


def make_theta_risk_plot(exp_dir: Path, window: int = 150):
    """
    Gera o gráfico de timeline para theta (trust score) e risco,
    ambos suavizados com média móvel de 'window' eventos.

    O gráfico é salvo como:
        <exp_dir>/fig-timeline-theta-risk.png
    com dpi=300 (qualidade para artigo).
    """
    timeline = load_timeline(exp_dir)
    steps = timeline["step"]
    theta = timeline["sb_theta"]
    risk = timeline["sb_risk"]

    # Suavização por média móvel
    theta_smooth = rolling_average(theta, window)
    risk_smooth = rolling_average(risk, window)

    plt.figure(figsize=(7, 4))
    plt.plot(
        steps,
        theta_smooth,
        label=f"Theta (trust score, média móvel {window} eventos)",
    )
    plt.plot(
        steps,
        risk_smooth,
        label=f"Risco (média móvel {window} eventos)",
        alpha=0.8,
    )
    plt.xlabel("Índice do evento")
    plt.ylabel("Score normalizado")
    plt.ylim(0.0, 1.0)
    plt.legend()
    plt.tight_layout()

    out_path = exp_dir / "fig-timeline-theta-risk.png"
    plt.savefig(out_path, dpi=300)
    plt.close()

    print(f"[OK] Gráfico timeline salvo em: {out_path}")


def main():
    exp_dir = get_latest_experiment_dir()
    print("[INFO] Usando experimento:", exp_dir)
    # Janela de 150 eventos dá um bom equilíbrio entre suavização e detalhe.
    make_theta_risk_plot(exp_dir, window=150)
    print("[INFO] Análise de plots concluída com sucesso.")


if __name__ == "__main__":
    main()
