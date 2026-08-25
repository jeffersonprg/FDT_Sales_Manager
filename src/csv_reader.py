import argparse
import json
from pathlib import Path

import pandas as pd

from src.services.importacao_csv_service import (
    ImportacaoCSVService,
    ResumoImportacaoCSV,
)
from src.utils.validator import preparar_dados_csv


def ler_csv(caminho_csv: str | Path) -> pd.DataFrame:
    caminho = Path(caminho_csv).expanduser().resolve()
    dados = pd.read_csv(caminho, encoding="utf-8-sig")
    return preparar_dados_csv(dados)


def importar_csv(
    caminho_csv: str | Path,
    tipo_validade_padrao: str = "VITALICIO",
    duracao_dias_padrao: int | None = None,
) -> ResumoImportacaoCSV:
    return ImportacaoCSVService.importar(
        caminho_csv,
        tipo_validade_padrao=tipo_validade_padrao,
        duracao_dias_padrao=duracao_dias_padrao,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Importa vendas CSV para o FDT Sales Manager."
    )
    parser.add_argument("caminho_csv", type=Path)
    parser.add_argument(
        "--tipo-validade",
        choices=("VITALICIO", "TEMPORARIO"),
        default="VITALICIO",
    )
    parser.add_argument("--duracao-dias", type=int)
    args = parser.parse_args()

    resumo = importar_csv(
        args.caminho_csv,
        tipo_validade_padrao=args.tipo_validade,
        duracao_dias_padrao=args.duracao_dias,
    )
    print(json.dumps(resumo.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
