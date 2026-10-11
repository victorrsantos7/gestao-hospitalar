import unittest
from datetime import date

from gestao_hospitalar.validacao_pacientes import (
    data_nascimento_valida,
    formatar_cpf,
    formatar_nome,
    formatar_telefone,
    nome_valido,
    normalizar_nome,
    normalizar_telefone,
    telefone_valido,
)


class ValidacaoPacientesTests(unittest.TestCase):
    def test_nome_aceita_unicode_hifen_e_apostrofo(self) -> None:
        self.assertTrue(nome_valido("Ana Beatriz D'Ávila-Souza"))
        self.assertEqual(normalizar_nome("  Ana   Beatriz  "), "Ana Beatriz")
        self.assertEqual(formatar_nome("Ana 2 @ Silva"), "Ana Silva")
        self.assertEqual(formatar_nome("Ana "), "Ana ")

    def test_nome_rejeita_numeros_e_simbolos(self) -> None:
        self.assertFalse(nome_valido("Ana 2"))
        self.assertFalse(nome_valido("Ana @ Silva"))
        self.assertFalse(nome_valido("   "))

    def test_telefone_aceita_fixo_e_celular(self) -> None:
        self.assertTrue(telefone_valido("1132345678"))
        self.assertTrue(telefone_valido("11998843763"))
        self.assertEqual(normalizar_telefone("(11) 99884-3763"), "11998843763")

    def test_telefone_rejeita_tamanho_invalido(self) -> None:
        self.assertFalse(telefone_valido("119988437"))
        self.assertFalse(telefone_valido("119988437633"))

    def test_data_aceita_data_real_nao_futura(self) -> None:
        self.assertTrue(data_nascimento_valida("2008-02-09", date(2026, 10, 11)))
        self.assertTrue(data_nascimento_valida("2026-10-11", date(2026, 10, 11)))

    def test_data_rejeita_data_invalida_e_futura(self) -> None:
        self.assertFalse(data_nascimento_valida("2026-02-30", date(2026, 10, 11)))
        self.assertFalse(data_nascimento_valida("2030-01-01", date(2026, 10, 11)))

    def test_aplica_mascaras_de_cpf_e_telefone(self) -> None:
        self.assertEqual(formatar_cpf("52998224725"), "529.982.247-25")
        self.assertEqual(formatar_telefone("11998843763"), "(11) 99884-3763")
        self.assertEqual(formatar_telefone("1132345678"), "(11) 3234-5678")

    def test_mascaras_limitam_apenas_a_apresentacao(self) -> None:
        self.assertEqual(formatar_cpf("529982247259"), "529.982.247-25")
        self.assertEqual(formatar_telefone("119988437633"), "(11) 99884-3763")
        self.assertFalse(telefone_valido("119988437633"))


if __name__ == "__main__":
    unittest.main()
