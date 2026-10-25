"""Valida a estrutura do template e, no modo estrito, sua qualidade Python."""

from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED_STRUCTURE = (
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "docs",
    "evals",
    "skills",
    "tools",
)
EXCLUDED_DIRECTORIES = {
    ".git",
    ".nox",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "env",
    "node_modules",
    "venv",
}
EXCLUDED_PATH_PREFIXES = {("docs", "raw")}
REQUIRED_SKILL_SECTIONS = (
    "Nome",
    "Objetivo",
    "Categoria",
    "Entradas",
    "Saídas",
    "Pré-condições",
    "Passos",
    "Critérios de sucesso",
    "Efeitos colaterais",
    "Exemplo",
    "Testes recomendados",
)


def has_module(module_name: str) -> bool:
    """Retorna se o módulo pode ser executado pelo interpretador atual."""
    return importlib.util.find_spec(module_name) is not None


def python_files() -> list[Path]:
    """Lista arquivos Python, ignorando diretórios que não fazem parte do código."""
    files: list[Path] = []
    for path in ROOT.rglob("*.py"):
        relative_path = path.relative_to(ROOT)
        if any(part in EXCLUDED_DIRECTORIES for part in relative_path.parts):
            continue
        if any(relative_path.parts[: len(prefix)] == prefix for prefix in EXCLUDED_PATH_PREFIXES):
            continue
        files.append(path)
    return sorted(files)


def run(command: list[str]) -> int:
    """Executa um comando sem shell e devolve seu código de saída."""
    print(f"Executando: {' '.join(command)}")
    completed = subprocess.run(command, cwd=ROOT, check=False)
    return completed.returncode


def validate_structure() -> bool:
    """Confirma a presença dos itens básicos do template."""
    print("Validando estrutura do projeto...")
    missing = [item for item in REQUIRED_STRUCTURE if not (ROOT / item).exists()]
    if missing:
        for item in missing:
            print(f"Erro: item obrigatório ausente: {item}")
        return False

    print("Estrutura básica válida.")
    return True


def validate_skills() -> bool:
    """Confirma que cada diretório de skill contém o documento mínimo esperado."""
    skill_directories = sorted(path for path in (ROOT / "skills").iterdir() if path.is_dir())
    valid = True
    for directory in skill_directories:
        skill_file = directory / "SKILL.md"
        if not skill_file.is_file():
            print(f"Erro: skill sem SKILL.md: {directory.relative_to(ROOT)}")
            valid = False
            continue

        content = skill_file.read_text(encoding="utf-8")
        missing_sections = [
            section for section in REQUIRED_SKILL_SECTIONS if f"## {section}" not in content
        ]
        if missing_sections:
            print(
                f"Erro: {skill_file.relative_to(ROOT)} sem seções: "
                f"{', '.join(missing_sections)}"
            )
            valid = False

    if valid:
        print("Skills válidas.")
    return valid


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Valida a estrutura; --strict também executa as verificações exigidas."
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exige pytest, ruff e validação das skills quando aplicáveis.",
    )
    args = parser.parse_args()

    if not validate_structure():
        return 1

    files = python_files()
    if not args.strict:
        if files and not has_module("ruff"):
            print("Lint não foi executado: ruff não está disponível.")
        elif files:
            print("Lint disponível, mas não executado no modo padrão.")
        print("Validação padrão concluída: somente a estrutura é bloqueante.")
        return 0

    failed = False
    missing_required_tool = False
    tests_directory = ROOT / "tests"
    if tests_directory.is_dir():
        if has_module("pytest"):
            failed = run([sys.executable, "-m", "pytest"]) != 0 or failed
        else:
            print("Erro: tests/ existe, mas pytest não está disponível.")
            missing_required_tool = True
    else:
        print("Nenhuma pasta tests/ encontrada; pytest não é exigido.")

    if files:
        if has_module("ruff"):
            targets = [str(path.relative_to(ROOT)) for path in files]
            failed = run([sys.executable, "-m", "ruff", "check", *targets]) != 0 or failed
        else:
            print("Erro: arquivos Python encontrados, mas ruff não está disponível.")
            missing_required_tool = True
    else:
        print("Nenhum arquivo Python encontrado; ruff não é exigido.")

    if not validate_skills():
        failed = True

    if failed:
        return 1
    if missing_required_tool:
        return 2

    print("Validação estrita concluída sem falhas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
