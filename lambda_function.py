import logging
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model.response import Response
from ask_sdk_model.audio import (
    PlayDirective, 
    PlayBehavior, 
    AudioItem, 
    Stream, 
    StopDirective
)

# Configuração de Log
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# --- Variáveis de Configuração ---
# URL de Streaming fornecida: 
STREAM_URL = "https://stm1.painelvox.xyz:6712/stream" 

# Identificador único para a sessão de áudio.
TOKEN = "transa_hits_token" 
SKILL_NAME = "Rádio Transa Hits FM 107,9"


# ---------------- Handlers de Intent ----------------

# 1. LaunchRequestHandler (Quando o usuário diz "Alexa, abra Transa Hits")
class LaunchRequestHandler(AbstractRequestHandler):
    """Lida com a LaunchRequest e a Intent de Resume."""
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        logger.info("Iniciando LaunchRequestHandler")
        
        speech_text = f"Iniciando {SKILL_NAME}. Aproveite!"
        
        # 1. Cria o objeto Stream com a URL
        stream = Stream(
            token=TOKEN,
            url=STREAM_URL,
            offset_in_milliseconds=0
        )
        
        # 2. Cria o objeto AudioItem
        audio_item = AudioItem(stream=stream)
        
        # 3. Cria a diretiva PlayDirective para começar a tocar o áudio
        play_directive = PlayDirective(
            play_behavior=PlayBehavior.REPLACE_ALL,
            audio_item=audio_item
        )
        
        # Retorna a resposta com a diretiva de áudio
        return handler_input.response_builder.speak(speech_text).add_directive(play_directive).response

# 2. BuiltInStopCancelPauseHandler (Para parar ou pausar a rádio)
class BuiltInStopCancelPauseHandler(AbstractRequestHandler):
    """Lida com Intents AMAZON.CancelIntent, AMAZON.StopIntent e AMAZON.PauseIntent."""
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input) or
                is_intent_name("AMAZON.PauseIntent")(handler_input))

    def handle(self, handler_input):
        logger.info("Iniciando BuiltInStopCancelPauseHandler")
        
        speech_text = f"{SKILL_NAME} pausada. Até logo!"
        
        # Cria a diretiva StopDirective para parar o áudio
        # StopDirective é usada para parar a reprodução atual do AudioPlayer.
        return handler_input.response_builder.speak(speech_text).add_directive(
            StopDirective()).response

# 3. BuiltInResumeIntentHandler (Para continuar tocando a rádio)
class BuiltInResumeIntentHandler(AbstractRequestHandler):
    """Lida com a Intent AMAZON.ResumeIntent."""
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.ResumeIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("Iniciando BuiltInResumeIntentHandler")
        # Reutiliza a lógica de LaunchRequestHandler para reiniciar o stream
        return LaunchRequestHandler().handle(handler_input) 

# 4. FallbackIntentHandler (Para lidar com requisições que não correspondem a nenhuma Intent)
class FallbackIntentHandler(AbstractRequestHandler):
    """Lida com a Intent AMAZON.FallbackIntent."""
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("Iniciando FallbackIntentHandler")
        speech_text = f"Desculpe, não entendi. Você pode dizer 'Alexa, toque {SKILL_NAME}'."
        return handler_input.response_builder.speak(speech_text).response

# 5. SessionEndedRequest (Quando a sessão termina)
class SessionEndedRequestHandler(AbstractRequestHandler):
    """Lida com a SessionEndedRequest."""
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        logger.info("Iniciando SessionEndedRequestHandler")
        # Sem resposta de voz necessária
        return handler_input.response_builder.response


# ---------------- Skill Builder e Lambda Handler ----------------

sb = SkillBuilder()

# Adiciona todos os Handlers criados
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(BuiltInStopCancelPauseHandler())
sb.add_request_handler(BuiltInResumeIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# O handler principal que a AWS Lambda chamará
handler = sb.lambda_handler()