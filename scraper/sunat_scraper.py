import logging
from playwright.async_api import async_playwright, TimeoutError

logger = logging.getLogger(__name__)

SUNAT_URL = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/FrameCriterioBusquedaWeb.jsp"


class SunatRUCClient:
    def __init__(self, browser: str = "edge", headless: bool = False):
        self.browser = browser
        self.headless = headless

        self.playwright = None
        self.context = None
        self.page = None

        self.dialog_alert = False
        self.dialog_msg = ""

    async def start(self):
        if self.browser == "edge":
            browser_channel = "msedge"
            user_data_dir = "edge_profile"
        elif self.browser == "chrome":
            browser_channel = "chrome"
            user_data_dir = "chrome_profile"
        else:
            raise ValueError("browser debe ser 'edge' o 'chrome'")

        self.playwright = await async_playwright().start()
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            channel=browser_channel,
            headless=self.headless,
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        self.page = await self.context.new_page()
        self.page.on("dialog", self._handle_dialog)
        await self.page.goto(SUNAT_URL)

    async def close(self):
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()

    async def _handle_dialog(self, dialog):
        self.dialog_msg = (dialog.message or "").lower()
        self.dialog_alert = True
        await dialog.accept()

    def _reset_dialog_state(self):
        self.dialog_alert = False
        self.dialog_msg = ""

    @staticmethod
    def invalid_ruc(ruc: str) -> bool:
        if not ruc:
            return True
        txt = str(ruc).strip()
        return not txt.isdigit()

    @staticmethod
    def resultado_invalido(motivo: str) -> dict:
        return {
            "ruc_razonSocial": "",
            "tipoContribuyente": "",
            "nombreComercial": "",
            "fechaInscripcion": "",
            "fechaInicioAct": "",
            "estadoContribuyente": "",
            "condicionContribuyente": "",
            "domicilioFiscal": "",
            "actividadEconomica": "",
            "validez": motivo
        }

    async def _leer_campo(self, campo: str) -> str:
        xpath = f'//h4[contains(text(), "{campo}")]/parent::div/following-sibling::div[1]/*[1]'
        try:
            return (await self.page.locator(f"xpath={xpath}").inner_text(timeout=800)).strip()
        except TimeoutError:
            return ""

    async def _obtener_datos(self) -> dict:
        etiquetas = {
            "ruc_razonSocial": "Número de RUC",
            "tipoContribuyente": "Tipo Contribuyente",
            "nombreComercial": "Nombre Comercial",
            "fechaInscripcion": "Fecha de Inscripción",
            "fechaInicioAct": "Fecha de Inicio de Acti",
            "estadoContribuyente": "Estado del Contribuyente",
            "condicionContribuyente": "Condición del Contribuyente",
            "domicilioFiscal": "Domicilio Fiscal",
            "actividadEconomica": "Actividad(es) Económica(s)"
        }
        datos = {k: await self._leer_campo(v) for k, v in etiquetas.items()}
        datos["validez"] = (
            "Desconocido - No se hallaron los campos"
            if all(not v for v in datos.values())
            else "RUC válido"
        )
        return datos

    async def consultar_ruc(self, ruc: str) -> dict:
        if self.invalid_ruc(ruc):
            return self.resultado_invalido("RUC inválido - formato incorrecto")

        self._reset_dialog_state()
        try:
            await self.page.click("#txtRuc")
            await self.page.keyboard.press("Control+A")
            await self.page.keyboard.press("Delete")
            await self.page.keyboard.type(ruc, delay=1)
            await self.page.click("#btnAceptar")
            await self.page.wait_for_load_state("domcontentloaded")

            if self.dialog_alert:
                logger.warning(f'RUC {ruc}: {self.dialog_msg}')
                return self.resultado_invalido(f"RUC inválido - {self.dialog_msg}")

            if SUNAT_URL in self.page.url:
                return self.resultado_invalido("Desconocido - URL SUNAT no coincide")

            datos = await self._obtener_datos()
            logger.info(f'RUC {ruc}: datos obtenidos')
            await self.page.go_back()
            return datos

        except Exception as e:
            logger.exception(f'RUC {ruc}: Error no identificado')
            return self.resultado_invalido("Desconocido - Error no identificado")