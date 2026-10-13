import unittest

from gestao_hospitalar.validacao_convenios import (
    TIPOS_CONVENIO,
    nome_convenio_valido,
    normalizar_nome_convenio,
    tipo_convenio_valido,
)


class ValidacaoConveniosTests(unittest.TestCase):
    def test_accepts_only_supported_types(self) -> None:
        self.assertTrue(all(tipo_convenio_valido(tipo) for tipo in TIPOS_CONVENIO))
        self.assertFalse(tipo_convenio_valido("empresarial"))

    def test_normalizes_and_validates_name(self) -> None:
        self.assertEqual(
            normalizar_nome_convenio("  Saude  Integral "),
            "Saude Integral",
        )
        self.assertTrue(nome_convenio_valido("Saude Integral"))
        self.assertFalse(nome_convenio_valido("123"))


if __name__ == "__main__":
    unittest.main()