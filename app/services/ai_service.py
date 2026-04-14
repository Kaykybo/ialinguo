import openai
import json
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY', 'sua-chave-aqui')


class AIService:

    BASE_SYSTEM_PROMPT = (
        "You are an English language tutor whose only purpose is to help the student practice English. "
        "Always respond in English. "
        "Never translate the user's text or reply in Portuguese. "
        "If the user writes in Portuguese or any other language, politely remind them that this session is only for English practice "
        "and that using another language will lower their fluency score. "
        "Do not answer unrelated questions or provide content outside the English learning task. "
        "If the user asks for something outside this scenario, refuse politely and steer the conversation back to English practice."
    )

    CONTEXTOS = {
        'restaurante': "You are a restaurant waiter in an English-speaking country. Be polite and help the customer with orders, menu questions, and basic restaurant interactions.",
        'academia': "You are a personal trainer at a gym in the USA. Talk about exercises, workout routines, health tips, and gym-related conversation.",
        'aeroporto': "You are an airport employee. Help the passenger with check-in, flight information, boarding gates, and travel procedures.",
        'hotel': "You are a hotel receptionist. Help with reservations, check-in, check-out, room details, and local hotel information.",
        'entrevista': "You are a recruiter conducting a job interview in English. Ask professional questions about experience, skills, and career goals.",
        'conversa livre': "You are a friendly English chat partner keeping the conversation natural and casual."
    }

    def _get_system_prompt(self, contexto):
        context_prompt = self.CONTEXTOS.get(contexto, self.CONTEXTOS['conversa livre'])
        return f"{self.BASE_SYSTEM_PROMPT} {context_prompt}"

    def _montar_messages(self, mensagem_aluno, contexto, historico):
        messages = [{"role": "system", "content": self._get_system_prompt(contexto)}]

        for msg in historico[-5:]:
            role = "user" if msg['remetente'] == 'aluno' else "assistant"
            messages.append({"role": role, "content": msg['texto']})

        messages.append({"role": "user", "content": mensagem_aluno})
        return messages

    def gerar_resposta(self, mensagem_aluno, contexto='conversa livre', historico=[]):
        try:
            messages = self._montar_messages(mensagem_aluno, contexto, historico)

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=200,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"Erro na API OpenAI: {e}")
            return "I'm sorry, I'm having trouble responding right now. Please try again."

    def gerar_feedback(self, conversa_texto, contexto):
        try:
            prompt = f"""
            Analyze the following English conversation of a Brazilian student learning English.
            Conversation context: {contexto}

            Conversation:
            {conversa_texto}

            CRITICAL EVALUATION RULES:
            - FIRST: Check if the student actually participated. If there are NO student messages (only AI messages), give nota_fluencia = 1 and explain "No student participation detected. Cannot evaluate fluency without responses."
            - If the student only gave minimal responses (single words like "yes", "no", "ok" without meaningful conversation), give nota_fluencia = 2 and explain lack of engagement.
            - If the student used Portuguese or any non-English language, give nota_fluencia = 1 and emphasize this is unacceptable.
            - Only give scores above 5 if the student actively participated with multiple meaningful English responses.
            - Good scores (7-10) require substantial participation with varied vocabulary and sentence structures.

            Provide structured feedback in JSON with:
            1. pontos_positivos: A single string summarizing what the student did well (or "No participation to evaluate" if no responses)
            2. pontos_melhoria: A single string summarizing what needs improvement (focus on participation if no responses given)
            3. nota_fluencia: A score from 1 to 10 based STRICTLY on participation and English usage quality
            4. dicas: 2-3 specific tips for improvement

            Respond only with valid JSON.
            """

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an English teacher specializing in feedback for Brazilian students."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.5
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            print(f"Erro ao gerar feedback: {e}")
            return {
                "pontos_positivos": "You practiced English conversation.",
                "pontos_melhoria": "Keep practicing to improve.",
                "nota_fluencia": 5,
                "dicas": ["Practice more", "Listen to native speakers", "Repeat out loud"]
            }
