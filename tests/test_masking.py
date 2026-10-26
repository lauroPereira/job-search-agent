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
    ("text", "expected"),
    [
        ("Celular 11 9 8765-4321", "Celular [telefone]"),
        ("Celular +5511987654321", "Celular [telefone]"),
        ("Celular +55 11 98765 4321", "Celular [telefone]"),
        ("Celular 98765-4321", "Celular [telefone]"),
        ("Fixo 21 3456 7890", "Fixo [telefone]"),
        ("CPF 123 456 789 09 com espaços", "CPF [cpf] com espaços"),
    ],
)
def test_other_phone_and_cpf_forms_are_masked(text: str, expected: str) -> None:
    assert mask(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "Trabalhei de 2019-2023 no Banco Aurora",
        "Período 2019 2023",
        "Período 1998-2004",
        "teste 1234 5678",
        "Ramal 3456-7890 sem DDD",
    ],
)
def test_year_ranges_and_number_pairs_stay(text: str) -> None:
    assert mask(text) == text


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
