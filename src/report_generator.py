import argparse
from datetime import date
from pathlib import Path

from src.services.relatorio_html_service import RelatorioHTMLService


def _data_iso(valor: str) -> date:
    try:
        return date.fromisoformat(valor)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "Use datas no formato AAAA-MM-DD."
        ) from error


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gera o relatório comercial HTML do FDT Sales Manager."
    )
    parser.add_argument("--saida", type=Path)
    parser.add_argument("--inicio", type=_data_iso)
    parser.add_argument("--fim", type=_data_iso)
    parser.add_argument("--titulo")
    parser.add_argument("--idioma", choices=("pt", "en", "es"))
    args = parser.parse_args()

    caminho = RelatorioHTMLService.gerar(
        caminho_saida=args.saida,
        data_inicio=args.inicio,
        data_fim=args.fim,
        titulo=args.titulo,
        idioma=args.idioma,
    )
    print(caminho)


if __name__ == "__main__":
    main()
