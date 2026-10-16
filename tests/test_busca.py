import unittest

from gestao_hospitalar.busca import filtrar_registros, normalizar_busca


class BuscaTests(unittest.TestCase):
    REGISTROS = [
        {"id": "1", "nome": "José Antônio", "telefone": "(11) 91234-5678"},
        {"id": "2", "nome": "Maria Souza", "telefone": "(21) 99876-5432"},
    ]

    def test_normaliza_acento_e_caixa(self) -> None:
        self.assertEqual(normalizar_busca("  JOSÉ "), "jose")

    def test_termo_vazio_retorna_todos(self) -> None:
        self.assertEqual(filtrar_registros(self.REGISTROS, "  "), self.REGISTROS)

    def test_busca_ignora_acento(self) -> None:
        resultado = filtrar_registros(self.REGISTROS, "jose antonio")
        self.assertEqual([r["id"] for r in resultado], ["1"])

    def test_busca_em_qualquer_campo(self) -> None:
        resultado = filtrar_registros(self.REGISTROS, "99876")
        self.assertEqual([r["id"] for r in resultado], ["2"])

    def test_sem_correspondencia(self) -> None:
        self.assertEqual(filtrar_registros(self.REGISTROS, "xyz"), [])


if __name__ == "__main__":
    unittest.main()
