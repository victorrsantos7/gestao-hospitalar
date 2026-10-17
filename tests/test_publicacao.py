import logging
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gestao_hospitalar import logging_config
from gestao_hospitalar.configuracao import ORIGENS_LOCAIS, origens_cors

RAIZ = Path(__file__).resolve().parent.parent


class OrigensCorsTests(unittest.TestCase):
    def test_sem_valor_usa_somente_as_portas_locais(self) -> None:
        for valor in (None, "", "   ", " , "):
            with self.subTest(valor=valor):
                self.assertEqual(origens_cors(valor), ORIGENS_LOCAIS)

    def test_lista_informada_substitui_o_padrao(self) -> None:
        self.assertEqual(
            origens_cors("https://app.reflex.dev/, http://localhost:3000"),
            ["https://app.reflex.dev", "http://localhost:3000"],
        )

    def test_asterisco_libera_todas_as_origens(self) -> None:
        self.assertEqual(origens_cors("*"), ["*"])

    def test_padrao_nao_e_alterado_por_quem_chama(self) -> None:
        origens_cors(None).append("http://x")

        self.assertEqual(origens_cors(None), ORIGENS_LOCAIS)


class LogEmSaidaPadraoTests(unittest.TestCase):
    def setUp(self) -> None:
        raiz = logging.getLogger("gestao_hospitalar")
        estado = (list(raiz.handlers), raiz.propagate, raiz.level)
        raiz.handlers.clear()

        def restaurar() -> None:
            for handler in list(raiz.handlers):
                handler.close()
            raiz.handlers[:] = estado[0]
            raiz.propagate, raiz.level = estado[1], estado[2]

        self.addCleanup(restaurar)
        self.raiz = raiz

    def _handler(self, ambiente: dict[str, str]) -> logging.Handler:
        with patch.dict(os.environ, ambiente, clear=False):
            logging_config.get_logger("teste")
        self.assertEqual(len(self.raiz.handlers), 1)
        return self.raiz.handlers[0]

    def test_traco_escolhe_a_saida_padrao(self) -> None:
        handler = self._handler({"GESTAO_LOG_FILE": "-"})

        self.assertNotIsInstance(handler, logging.FileHandler)
        self.assertIsInstance(handler, logging.StreamHandler)

    def test_pasta_sem_escrita_cai_para_a_saida_padrao(self) -> None:
        with tempfile.NamedTemporaryFile() as arquivo:
            # um arquivo no lugar da pasta faz o mkdir falhar com OSError
            handler = self._handler(
                {"GESTAO_LOG_FILE": str(Path(arquivo.name) / "sub" / "app.log")}
            )

        self.assertNotIsInstance(handler, logging.FileHandler)

    def test_caminho_valido_continua_gravando_em_arquivo(self) -> None:
        with tempfile.TemporaryDirectory() as pasta:
            handler = self._handler({"GESTAO_LOG_FILE": str(Path(pasta) / "app.log")})
            self.assertIsInstance(handler, logging.FileHandler)
            handler.close()


class ArquivosDePublicacaoTests(unittest.TestCase):
    def test_cloud_yml_nunca_envia_o_env_local(self) -> None:
        texto = (RAIZ / "cloud.yml").read_text(encoding="utf-8")

        self.assertIn("envfile: .env.cloud", texto)

    def test_arquivos_com_segredo_ficam_fora_do_git(self) -> None:
        linhas = (RAIZ / ".gitignore").read_text(encoding="utf-8").splitlines()

        self.assertIn(".env", linhas)
        self.assertIn(".env.cloud", linhas)

    def test_modelo_da_nuvem_nao_traz_credenciais(self) -> None:
        texto = (RAIZ / ".env.cloud.example").read_text(encoding="utf-8")
        ativas = [
            linha for linha in texto.splitlines() if linha and not linha.startswith("#")
        ]

        self.assertFalse(any("XANO_TEST_" in linha for linha in ativas))
        self.assertFalse(any(linha.startswith("XANO_API_TOKEN") for linha in ativas))
        self.assertIn("GESTAO_LOG_FILE=-", ativas)


if __name__ == "__main__":
    unittest.main()
