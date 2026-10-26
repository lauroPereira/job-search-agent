"""Masking with synthetic examples of each pattern and of a name of the list."""

import pytest

from job_search_agent.masking import fold, mask

NAMES = ("Ana Exemplo", "Fábio Demonstração")


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Escreva para ana.exemplo@example.com hoje", "Escreva para [email] hoje"),
        ("Perfil: https://www.linkedin.com/in/pessoa-ficticia-123", "Perfil: [perfil]"),
        ("Código em github.com/pessoa-ficticia/projeto", "Código em [perfil]"),
        ("CPF 123.456.789-09 no cadastro", "CPF [cpf] no cadastro"),
        ("CPF 12345678909 sem pontos", "CPF [cpf] sem pontos"),
        ("Ligue +55 (11) 91234-5678 amanhã", "Ligue [telefone] amanhã"),
        ("WhatsApp 11 91234-5678", "WhatsApp [telefone]"),
        ("Fixo (21) 3456-7890", "Fixo [telefone]"),
        ("Conta 0001234567890", "Conta [numero]"),
    ],
)
def test_each_pattern_is_masked(text: str, expected: str) -> None:
    assert mask(text) == expected


@pytest.mark.parametrize(
    "text",
    ["Conversei com Ana Exemplo", "conversei com ANA   exemplo", "Conversei com Âna Exêmplo"],
)
def test_listed_name_is_masked_without_accent_or_case(text: str) -> None:
    assert mask(text, NAMES) == text[:14] + "[pessoa]"


def test_accented_name_matches_plain_text() -> None:
    assert mask("Reunião com fabio demonstracao.", NAMES) == "Reunião com [pessoa]."


def test_company_names_dates_and_scores_stay() -> None:
    text = "Banco Aurora, entrevista em 2026-03-16, nota 8.5, Anaconda e Ana Exemplar"
    assert mask(text, NAMES) == text


def test_fold_keeps_positions() -> None:
    assert fold("Fábio Ç") == "fabio c"
    assert len(fold("Demonstração")) == len("Demonstração")
