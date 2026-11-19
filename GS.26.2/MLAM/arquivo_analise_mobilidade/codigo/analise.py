"""Análise reprodutível da base horária Bike Sharing (UCI)."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

# Geração do relatório editável em Word.
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# Caminhos do projeto e estilo compartilhado dos gráficos
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "dados" / "bike_sharing_hour.csv"
FIG = ROOT / "figuras"
FIG.mkdir(exist_ok=True)
plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titleweight": "bold",
        "figure.facecolor": "#f5f5f0",
        "axes.facecolor": "#ffffff",
        "savefig.facecolor": "#f5f5f0",
    }
)
GREEN, DARK, MUTED = "#4f7c2f", "#263124", "#747b70"


# Funções auxiliares reutilizáveis
def num(x):
    return float(x) if np.isfinite(x) else None


def save_chart(fig, filename):
    fig.savefig(FIG / filename, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main():
    # 01 — carregar a base original e validar as colunas necessárias.
    df = pd.read_csv(DATA)
    cols = ["cnt", "temp", "hum", "windspeed", "hr"]
    assert set(cols).issubset(df.columns)
    y = df.cnt.astype(float)
    n = len(df)
    mean, median, sd = y.mean(), y.median(), y.std(ddof=0)

    # 02 — probabilidades sob a hipótese normal indicada no enunciado.
    p_less_mean = stats.norm.cdf(mean, loc=mean, scale=sd)
    p_greater_median = stats.norm.sf(median, loc=mean, scale=sd)

    # 03 — testes Z unilaterais com semente fixa para reproduzir as amostras.
    rng = np.random.default_rng(2026)
    tests = []
    for size, alpha, alternative in [(20, 0.06, "less"), (25, 0.09, "greater")]:
        sample = rng.choice(y.to_numpy(), size=size, replace=False)
        z = (sample.mean() - mean) / (sd / np.sqrt(size))
        p = stats.norm.cdf(z) if alternative == "less" else stats.norm.sf(z)
        critical = (
            stats.norm.ppf(alpha)
            if alternative == "less"
            else stats.norm.ppf(1 - alpha)
        )
        tests.append(
            {
                "n": size,
                "alpha": alpha,
                "alternative": alternative,
                "sample_mean": num(sample.mean()),
                "mu0": num(mean),
                "sigma": num(sd),
                "z": num(z),
                "p": num(p),
                "critical": num(critical),
                "reject": bool(p < alpha),
            }
        )

    # 04 — análise bivariada: temperatura normalizada e locações por hora.
    x = df.temp.astype(float)
    lr = stats.linregress(x, y)
    cov = np.cov(x, y, ddof=1)[0, 1]
    grid = np.linspace(x.min(), x.max(), 200)
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.scatter(
        x, y, s=8, alpha=0.34, color="#386b2c", edgecolors="none", label="Observações"
    )
    ax.plot(
        grid,
        lr.intercept + lr.slope * grid,
        color=DARK,
        lw=2.5,
        label="Regressão linear",
    )
    ax.set(
        title="Temperatura e quantidade de locações por hora",
        xlabel="Temperatura (escala normalizada)",
        ylabel="Locações de bicicletas por hora",
    )
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.15)
    save_chart(fig, "dispersao_temperatura_locacoes.png")

    # 05 — regressão linear múltipla com três preditores quantitativos.
    predictors = ["temp", "hum", "windspeed"]
    X = df[predictors].astype(float).to_numpy()
    Xd = np.column_stack([np.ones(n), X])
    beta = np.linalg.lstsq(Xd, y.to_numpy(), rcond=None)[0]
    fitted = Xd @ beta
    residual = y.to_numpy() - fitted
    sse = float(residual @ residual)
    sst = float(((y.to_numpy() - mean) ** 2).sum())
    r2 = 1 - sse / sst
    k = len(predictors)
    f_stat = ((sst - sse) / k) / (sse / (n - k - 1))
    f_p = stats.f.sf(f_stat, k, n - k - 1)
    adj_r2 = 1 - (1 - r2) * (n - 1) / (n - k - 1)
    pred_input = df[predictors].mean().to_numpy()
    pred_count = float(np.r_[1, pred_input] @ beta)
    covmat = df[predictors].cov()
    corrmat = df[predictors].corr()

    # 06 — regressão logística; demanda alta é cnt acima da mediana.
    cutoff = float(y.median())
    target = (y > cutoff).astype(int)
    logit_predictors = ["temp", "hum", "windspeed", "hr"]
    xtrain, xtest, ytrain, ytest = train_test_split(
        df[logit_predictors].astype(float),
        target,
        test_size=0.20,
        random_state=42,
        stratify=target,
    )
    model = make_pipeline(
        StandardScaler(), LogisticRegression(max_iter=2000, random_state=42)
    )
    model.fit(xtrain, ytrain)
    predicted = model.predict(xtest)
    example = xtest.iloc[0]
    example_probability = float(model.predict_proba(xtest.iloc[[0]])[0, 1])
    example_class = int(example_probability >= 0.5)
    matrix = confusion_matrix(ytest, predicted, labels=[0, 1])
    accuracy = accuracy_score(ytest, predicted)
    scaler, classifier = (
        model.named_steps["standardscaler"],
        model.named_steps["logisticregression"],
    )
    # Coeficientes no espaço original: beta_j / escala_j; intercepto ajustado.
    raw_coef = classifier.coef_[0] / scaler.scale_
    raw_intercept = classifier.intercept_[0] - np.sum(
        classifier.coef_[0] * scaler.mean_ / scaler.scale_
    )

    # 07 — gerar gráficos usados na interface e no relatório.
    corr_all = df[["cnt", "temp", "hum", "windspeed", "hr"]].corr()
    fig, ax = plt.subplots(figsize=(7, 5.3))
    im = ax.imshow(corr_all, cmap="RdYlGn", vmin=-1, vmax=1)
    labs = ["Locações", "Temperatura", "Umidade", "Vento", "Hora"]
    ax.set_xticks(range(len(labs)), labs, rotation=30, ha="right")
    ax.set_yticks(range(len(labs)), labs)
    for i in range(len(labs)):
        for j in range(len(labs)):
            ax.text(
                j,
                i,
                f"{corr_all.iloc[i,j]:.2f}",
                ha="center",
                va="center",
                fontsize=9,
                color="white" if abs(corr_all.iloc[i, j]) > 0.68 else DARK,
            )
    ax.set_title("Correlação de Pearson entre variáveis")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    save_chart(fig, "matriz_correlacao.png")

    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    labels = ["Temperatura", "Umidade", "Velocidade do vento"]
    mat = corrmat.to_numpy()
    im = ax.imshow(mat, cmap="RdYlGn", vmin=-1, vmax=1)
    ax.set_xticks(range(3), labels, rotation=24, ha="right")
    ax.set_yticks(range(3), labels)
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{mat[i,j]:.2f}", ha="center", va="center", color=DARK)
    ax.set_title("Correlação entre preditores da regressão múltipla")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    save_chart(fig, "correlacao_preditores.png")

    # Dispersão multivariada em pares de preditores, colorida pelo desfecho.
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.4))
    pairs = [("temp", "hum"), ("temp", "windspeed"), ("hum", "windspeed")]
    for ax, (a, b) in zip(axes, pairs):
        points = ax.scatter(
            df[a],
            df[b],
            c=y,
            cmap="Greens",
            vmin=0,
            vmax=y.max(),
            s=6,
            alpha=0.55,
            edgecolors="none",
        )
        ax.set_xlabel(a)
        ax.set_ylabel(b)
    fig.suptitle(
        "Dispersões entre variáveis quantitativas (cor = locações)", fontweight="bold"
    )
    fig.colorbar(points, ax=axes, label="Locações/hora", fraction=0.025, pad=0.02)
    save_chart(fig, "dispersao_multivariada.png")

    fig, ax = plt.subplots(figsize=(5, 3.5))
    ax.imshow(matrix, cmap="Greens", vmin=0, vmax=matrix.max())
    ax.set_xticks([0, 1], ["Prevista baixa", "Prevista alta"])
    ax.set_yticks([0, 1], ["Real baixa", "Real alta"])
    for i in range(2):
        for j in range(2):
            ax.text(
                j,
                i,
                str(matrix[i, j]),
                ha="center",
                va="center",
                fontsize=14,
                color="white" if matrix[i, j] > matrix.max() * 0.55 else DARK,
            )
    ax.set_title(f"Matriz de confusão · acurácia {accuracy:.1%}")
    save_chart(fig, "matriz_confusao.png")

    # 08 — reunir medidas para o relatório, a interface e o arquivo JSON.
    results = {
        "source": "UCI Bike Sharing Dataset (hour.csv), doi:10.24432/C5W894",
        "source_url": "https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset",
        "n": n,
        "missing": int(df.isna().sum().sum()),
        "years": [2011, 2012],
        "count": {
            "mean": num(mean),
            "median": num(median),
            "std_population": num(sd),
            "min": int(y.min()),
            "max": int(y.max()),
        },
        "probability": {
            "less_than_mean": num(p_less_mean),
            "greater_than_median": num(p_greater_median),
            "median_z": num((median - mean) / sd),
        },
        "hypothesis_tests": tests,
        "bivariate": {
            "x": "temp",
            "y": "cnt",
            "covariance": num(cov),
            "pearson_r": num(lr.rvalue),
            "p_value": num(lr.pvalue),
            "slope": num(lr.slope),
            "intercept": num(lr.intercept),
            "r2": num(lr.rvalue**2),
            "f": num(lr.rvalue**2 / (1 - lr.rvalue**2) * (n - 2)),
            "f_p": num(
                stats.f.sf(lr.rvalue**2 / (1 - lr.rvalue**2) * (n - 2), 1, n - 2)
            ),
            "prediction_at_mean_temp": num(lr.intercept + lr.slope * x.mean()),
            "covariance_matrix": df[["temp", "cnt"]].cov().to_dict(),
        },
        "multivariate": {
            "predictors": predictors,
            "coefficients": {
                "intercept": num(beta[0]),
                **{p: num(c) for p, c in zip(predictors, beta[1:])},
            },
            "r2": num(r2),
            "adjusted_r2": num(adj_r2),
            "f": num(f_stat),
            "f_p": num(f_p),
            "df_model": k,
            "df_resid": n - k - 1,
            "prediction_at_mean_predictors": num(pred_count),
            "input_means": {p: num(v) for p, v in zip(predictors, pred_input)},
            "covariance": covmat.to_dict(),
            "correlation": corrmat.to_dict(),
        },
        "logistic": {
            "target_definition": f"cnt > mediana ({cutoff:g} locações/hora)",
            "cutoff": cutoff,
            "predictors": logit_predictors,
            "coefficients": {
                "intercept": num(raw_intercept),
                **{p: num(c) for p, c in zip(logit_predictors, raw_coef)},
            },
            "confusion_matrix": matrix.tolist(),
            "accuracy": num(accuracy),
            "test_size": len(ytest),
            "class_balance": {
                "baixa": int((target == 0).sum()),
                "alta": int((target == 1).sum()),
            },
            "example": {
                "inputs": {p: num(example[p]) for p in logit_predictors},
                "probability_high": example_probability,
                "predicted_class": "alta" if example_class else "baixa",
                "observed_class": "alta" if int(ytest.iloc[0]) else "baixa",
            },
        },
        "figures": [
            "figuras/dispersao_temperatura_locacoes.png",
            "figuras/matriz_correlacao.png",
            "figuras/dispersao_multivariada.png",
            "figuras/correlacao_preditores.png",
            "figuras/matriz_confusao.png",
        ],
    }
    (ROOT / "resultados.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    create_report(results, df, corr_all, covmat, corrmat, matrix)
    print(
        json.dumps(
            {
                "n": n,
                "mean": mean,
                "median": median,
                "p_greater_median": p_greater_median,
                "tests": tests,
                "r": lr.rvalue,
                "simple_r2": lr.rvalue**2,
                "multi_r2": r2,
                "f": f_stat,
                "logit_accuracy": accuracy,
                "confusion": matrix.tolist(),
            },
            indent=2,
        )
    )


# Geração do relatório editável em Word.
def create_report(r, df, corr_all, covmat, corrmat, confusion):
    # Configurar página, tipografia, cabeçalho e rodapé do documento.
    out = ROOT / "relatorio_estatistico.docx"
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.65)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)
    styles = doc.styles
    styles["Normal"].font.name = "Calibri"
    styles["Normal"]._element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    styles["Normal"].font.size = Pt(10.5)
    styles["Normal"].font.color.rgb = RGBColor(45, 51, 43)
    styles["Normal"].paragraph_format.space_after = Pt(7)
    for name, size, color in [
        ("Title", 28, "263124"),
        ("Heading 1", 19, "263124"),
        ("Heading 2", 13, "547529"),
    ]:
        style = styles[name]
        style.font.name = "Calibri"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(color)
    header = section.header.paragraphs[0]
    header.text = "TRABALHO ACADÊMICO  /  MLAM                             ANÁLISE DE MOBILIDADE"
    header.style = "Caption"
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run("Bike Sharing Dataset · UCI Machine Learning Repository · ")
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    footer._p.append(field)

    def shade(cell, fill):
        pr = cell._tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:fill"), fill)
        pr.append(shd)

    def title(kicker, heading, subtitle=None):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        run = p.add_run(kicker.upper())
        run.bold = True
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor.from_string("6F8750")
        doc.add_heading(heading, level=1)
        if subtitle:
            p = doc.add_paragraph(subtitle)
            p.paragraph_format.space_after = Pt(14)
            for run in p.runs:
                run.italic = True
                run.font.color.rgb = RGBColor.from_string("73796F")

    def para(text):
        p = doc.add_paragraph(text)
        p.paragraph_format.line_spacing = 1.12
        return p

    def picture(filename, width=6.25):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(FIG / filename), width=Inches(width))

    def matrix_table(data, headers, rows, digits=3):
        table = doc.add_table(rows=1, cols=len(headers) + 1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.style = "Light Shading Accent 1"
        for i, value in enumerate([""] + headers):
            table.rows[0].cells[i].text = str(value)
        for label, values in zip(rows, data):
            cells = table.add_row().cells
            cells[0].text = label
            for i, value in enumerate(values, 1):
                cells[i].text = f"{value:.{digits}f}"
        for row in table.rows:
            for cell in row.cells:
                cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                for p in cell.paragraphs:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for run in p.runs:
                        run.font.size = Pt(9)
        doc.add_paragraph().paragraph_format.space_after = Pt(1)

    def bullet(text):
        doc.add_paragraph(text, style="List Bullet")

    # Capa: título, contexto e resumo da base.
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(42)
    run = p.add_run("GLOBAL SOLUTION  /  TRABALHO ACADÊMICO · MLAM")
    run.bold = True
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor.from_string("6F8750")
    doc.add_paragraph("Mobilidade urbana\nem números", style="Title")
    p = doc.add_paragraph("Análise da demanda horária por bicicletas compartilhadas")
    p.paragraph_format.space_after = Pt(22)
    for run in p.runs:
        run.font.size = Pt(15)
        run.font.color.rgb = RGBColor.from_string("73796F")
    doc.add_heading("Pergunta de investigação", level=2)
    para(
        "Como condições meteorológicas e temporais se associam à demanda horária de bicicletas compartilhadas, e de que forma esses dados podem apoiar o planejamento da mobilidade ativa?"
    )
    doc.add_heading("Base e escopo", level=2)
    para(
        f"Bike Sharing Dataset, disponibilizado pelo UCI Machine Learning Repository: {r['n']:,} observações horárias do sistema Capital Bikeshare em Washington, D.C., nos anos de 2011 e 2012. A base contém contagens de locações e atributos de clima e calendário; não há valores ausentes nem dados pessoais."
    )
    cover = doc.add_table(rows=2, cols=3)
    cover.style = "Light Shading Accent 1"
    values = [
        ["17.379", "189,46", "142"],
        ["registros", "média de locações/h", "mediana de locações/h"],
    ]
    for i in range(2):
        for j in range(3):
            cell = cover.cell(i, j)
            cell.text = values[i][j]
            if i == 0:
                shade(cell, "EAF1E0")
                for run in cell.paragraphs[0].runs:
                    run.bold = True
                    run.font.size = Pt(15)
                    run.font.color.rgb = RGBColor.from_string("3E542D")
            else:
                for run in cell.paragraphs[0].runs:
                    run.font.size = Pt(9)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()
    doc.add_heading("Síntese", level=2)
    para(
        f"A temperatura apresenta associação positiva moderada com as locações (r = {r['bivariate']['pearson_r']:.3f}). O modelo linear múltiplo com três variáveis climáticas explica {r['multivariate']['r2']:.1%} da variação. A regressão logística para demanda acima da mediana alcançou {r['logistic']['accuracy']:.1%} de acurácia no conjunto de teste."
    )
    p = para(
        "Os dados são históricos e de uma cidade dos Estados Unidos. Os resultados descrevem associações, não comprovam causalidade e não devem ser generalizados diretamente para cidades brasileiras."
    )
    for run in p.runs:
        run.italic = True
        run.font.color.rgb = RGBColor.from_string("73796F")
    para(
        "Fonte: Fanaee-T, H.; Gama, J. Bike Sharing Dataset. UCI Machine Learning Repository. DOI: 10.24432/C5W894."
    )

    # Seção 1: probabilidades e testes de hipótese.
    pval = r["probability"]
    doc.add_page_break()
    title(
        "01 / Probabilidade e testes de hipótese",
        "Probabilidade e hipóteses",
        "Distribuição normal assumida conforme o enunciado",
    )
    para(
        f"A variável analisada é a quantidade horária de locações (cnt), com média μ = {r['count']['mean']:.2f}, desvio padrão populacional σ = {r['count']['std_population']:.2f} e mediana observada igual a {r['count']['median']:.0f}."
    )
    doc.add_heading("Probabilidades", level=2)
    bullet(
        f"P(X < média) = {pval['less_than_mean']:.3f} ({pval['less_than_mean']:.1%}). Evento equiprovável: em uma distribuição normal simétrica, metade da área fica abaixo da média."
    )
    bullet(
        f"P(X > mediana) = {pval['greater_than_median']:.3f} ({pval['greater_than_median']:.1%}). Evento provável, pois a probabilidade ultrapassa 0,5. A mediana está abaixo da média, o que sugere assimetria à direita; a normalidade é uma simplificação assumida no exercício."
    )
    doc.add_heading("Testes Z unilaterais para a média", level=2)
    para(
        "Em ambos os testes, H₀: μ = μ₀, onde μ₀ é a média global da base; σ de referência é o desvio padrão populacional observado. Foram sorteadas amostras sem reposição usando a semente 2026 para permitir reprodução."
    )
    for i, t in enumerate(r["hypothesis_tests"], 1):
        alt = "μ < μ₀" if t["alternative"] == "less" else "μ > μ₀"
        decision = "não rejeitamos H₀" if not t["reject"] else "rejeitamos H₀"
        para(
            f"Teste {i}: H₁: {alt}; n = {t['n']}; α = {t['alpha']:.0%}; média amostral = {t['sample_mean']:.2f}; z = {t['z']:.3f}; p-valor = {t['p']:.3f}; valor crítico = {t['critical']:.3f}. Decisão: {decision}. Não há evidência estatística suficiente para a direção alternativa ao nível especificado."
        )
    para(
        "Limite: a base inteira foi tratada como população de referência didática e as amostras são subconjuntos dela. Isso não substitui uma amostragem independente de uma população externa."
    )

    # Seção 2: relação bivariada e regressão linear simples.
    b = r["bivariate"]
    doc.add_page_break()
    title(
        "02 / Análise bivariada",
        "Temperatura e demanda",
        "Temperatura normalizada (0–1) e locações de bicicletas por hora",
    )
    picture("dispersao_temperatura_locacoes.png")
    para(
        f"Covariância amostral = {b['covariance']:.2f}; correlação de Pearson r = {b['pearson_r']:.3f} (p < 0,001). A relação é positiva e moderada: horas mais quentes tendem a registrar mais locações, embora haja grande dispersão e outros fatores influenciem a procura."
    )
    doc.add_heading("Regressão linear simples", level=2)
    para(
        f"Equação estimada: ŷ = {b['intercept']:.2f} + {b['slope']:.2f} × temperatura. R² = {b['r2']:.3f}; teste F(1, {r['n']-2}) = {b['f']:.1f}, p < 0,001. O modelo explica {b['r2']:.1%} da variação observada. O teste F identifica associação linear nesta amostra grande; isso não prova causalidade nem garante boa previsão individual."
    )
    para(
        f"Previsão na temperatura média observada ({df.temp.mean():.3f} na escala normalizada): {b['prediction_at_mean_temp']:.1f} locações por hora. É uma previsão média dentro do intervalo observado, não uma estimativa operacional."
    )

    # Seção 3: matrizes e regressão linear múltipla.
    m = r["multivariate"]
    doc.add_page_break()
    title(
        "03 / Análise multivariada",
        "Relações entre variáveis quantitativas",
        "Preditores: temperatura, umidade e velocidade do vento",
    )
    picture("dispersao_multivariada.png", width=6.25)
    para(
        "As dispersões mostram relações distintas de cada par de preditores com a quantidade horária de locações (cor). Temperatura e umidade têm correlação negativa fraca; umidade e vento, negativa moderada."
    )
    doc.add_heading("Matriz de covariância", level=2)
    matrix_table(
        covmat.to_numpy(), ["temp", "hum", "windspeed"], ["temp", "hum", "windspeed"], 4
    )
    doc.add_heading("Matriz de correlação de Pearson", level=2)
    matrix_table(
        corrmat.to_numpy(),
        ["temp", "hum", "windspeed"],
        ["temp", "hum", "windspeed"],
        3,
    )
    para(
        "As correlações entre os preditores indicam associações relativamente pequenas, com maior relação negativa entre umidade e vento (r = −0,290)."
    )

    doc.add_page_break()
    title(
        "03 / Modelo, adequação e previsão",
        "Regressão linear múltipla",
        "Resposta: quantidade de locações por hora (cnt)",
    )
    co = m["coefficients"]
    para("Equação estimada por mínimos quadrados:")
    eqp = para(
        f"ŷ = {co['intercept']:.2f} + ({co['temp']:.2f} × temp) + ({co['hum']:.2f} × hum) + ({co['windspeed']:.2f} × windspeed)"
    )
    for run in eqp.runs:
        run.bold = True
        run.font.color.rgb = RGBColor.from_string("547529")
    para(
        f"R² = {m['r2']:.3f}; R² ajustado = {m['adjusted_r2']:.3f}; teste F({m['df_model']}, {m['df_resid']}) = {m['f']:.1f}, p < 0,001. O conjunto dos três preditores está associado significativamente à contagem. O modelo explica {m['r2']:.1%} da variação; a maior parte permanece relacionada a fatores não incluídos, como hora, dia da semana e sazonalidade."
    )
    doc.add_heading("Previsão", level=2)
    para(
        f"Usando as médias observadas (temp = {m['input_means']['temp']:.3f}; hum = {m['input_means']['hum']:.3f}; windspeed = {m['input_means']['windspeed']:.3f}), a estimativa é {m['prediction_at_mean_predictors']:.1f} locações por hora."
    )
    para(
        "Limitações: a forma linear simplifica um fenômeno com padrões horários e sazonais; resíduos de observações horárias podem não ser independentes. Evite extrapolar além da faixa observada."
    )

    # Seção 4: classificação logística.
    l = r["logistic"]
    # Seção 5: conclusão, aplicação possível e limitações.
    doc.add_page_break()
    title(
        "04 / Classificação logística",
        "Classificar demanda alta",
        f"Demanda alta: cnt > mediana ({l['cutoff']:.0f} locações/hora); baixa: cnt ≤ mediana",
    )
    para(
        "O modelo utiliza temperatura, umidade, vento e hora. A divisão de treino e teste foi estratificada 80/20 (random_state = 42); padronização e ajuste foram feitos apenas no conjunto de treino."
    )
    co = l["coefficients"]
    terms = " + ".join(f"({co[p]:.3f} × {p})" for p in l["predictors"])
    para(
        f"Equação: logit(p) = {co['intercept']:.3f} + {terms}. A probabilidade estimada de demanda alta é p = 1/(1 + e⁻ᶻ); a classificação é alta quando p ≥ 0,5."
    )
    picture("matriz_confusao.png", width=4.8)
    matrix = l["confusion_matrix"]
    para(
        f"Matriz de confusão (linhas = classe real; colunas = classe prevista): TN = {matrix[0][0]}, FP = {matrix[0][1]}, FN = {matrix[1][0]}, TP = {matrix[1][1]}. Acurácia no conjunto de teste: {l['accuracy']:.1%} ({l['test_size']} observações). As classes estão aproximadamente equilibradas; ainda assim, a acurácia deve ser interpretada considerando o custo de falsos positivos e negativos."
    )
    ex = l["example"]
    vals = ", ".join(f"{p} = {v:.3f}" for p, v in ex["inputs"].items())
    para(
        f"Exemplo real do conjunto de teste: {vals}. Probabilidade estimada de demanda alta: {ex['probability_high']:.1%}; classificação prevista: {ex['predicted_class']} (observada: {ex['observed_class']})."
    )

    doc.add_page_break()
    title(
        "05 / Síntese",
        "Conclusões para apoiar decisões",
        "Resultados, aplicação possível e limites de uso",
    )
    for insight in [
        f"A contagem horária média foi {r['count']['mean']:.0f}, mas a amplitude de {r['count']['max']-r['count']['min']} locações revela demanda bastante variável.",
        f"Temperatura se associa positivamente às locações (r = {b['pearson_r']:.2f}); clima ajuda a contextualizar a procura.",
        f"O modelo múltiplo explica {m['r2']:.1%} da variação com clima. Incluir hora e calendário pode melhorar a descrição e a previsão.",
        f"A classificação da demanda alta alcançou {l['accuracy']:.1%} de acurácia no holdout; valide em períodos posteriores antes de qualquer uso operacional.",
    ]:
        bullet(insight)
    doc.add_heading("Aplicação possível", level=2)
    para(
        "Combinar previsão de demanda com redistribuição de bicicletas e monitoramento de estações nos horários de maior procura. Uma decisão local exige dados recentes, validação local, avaliação de equidade de cobertura e consulta aos usuários."
    )
    doc.add_heading("Limitações e referência", level=2)
    para(
        "A análise é observacional, baseada em Washington, D.C., em 2011–2012. As associações não provam causalidade nem se transferem diretamente para cidades brasileiras. A partição aleatória pode deixar horas próximas entre treino e teste; devido à autocorrelação temporal, a avaliação pode ser otimista e uma validação temporal é recomendada. Não há dados pessoais na base."
    )
    para(
        "Fanaee-T, H.; Gama, J. Bike Sharing Dataset. UCI Machine Learning Repository. DOI: 10.24432/C5W894. Dados originais coletados pelo Capital Bikeshare; atributos meteorológicos associados à base pelos autores."
    )

    doc.save(out)
    return out


if __name__ == "__main__":
    main()
